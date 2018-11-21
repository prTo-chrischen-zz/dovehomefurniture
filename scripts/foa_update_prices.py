import csv
import shopify
import math
import sys
from collections import defaultdict


# load the price data
prices = {}
with open(sys.argv[1], 'r') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        sku = row["Item"]
        price = row["MAP"]
        prices[sku] = price


from dove import categories, shopify_config
shopify_config.setup()


def parse_price(price_str):
    p = price_str.replace('$', '')
    p = p.replace(',', '')
    return int(float(p))

def calculate_price(price):
    if isinstance(price, str):
        d = parse_price(price)
    else:
        d = price
    # round to nearest 9
    return (int(math.ceil(d / 10.0)) * 10) - 1

sku_suffixes = [
    '-BED',
    '-TABLE',
    '-SECTIONAL',
    '-PK',
]

def add_tag(product, tag_to_add):
    existing_tags = [i.strip() for i in product.tags.split(',')]
    if tag_to_add not in existing_tags:
        existing_tags.append(tag_to_add)
        product.tags = existing_tags
        print " -> added MAP tag"
        product.save()

filter_args = {'vendor': 'Furniture of America'}
query_limit = 250

num_variants = 0
products_updated = 0
missing_prices = defaultdict(list)


num_products = shopify.Product.count(**filter_args)
# max 250 items per query, so need to do it by pages
for page in xrange(1, ((num_products-1)/query_limit)+2):
    products = shopify.Product.find(limit=query_limit, page=page,
                                    fields=['id', 'vendor', 'title', 'variants', 'tags'],
                                    **filter_args)

    for product in products:

        product_updated = False

        for variant in product.variants:
            # every variant should have a SKU
            sku = variant.sku

            if sku not in prices:
                # check to see if it has a suffix-less or suffix-ed version
                for suffix in sku_suffixes:
                    if sku.endswith(suffix):
                        possible_sku = sku[:-len(suffix)]
                    else:
                        possible_sku = sku + suffix
                    if possible_sku in prices:
                        print "[suffix]", sku, possible_sku
                        sku = possible_sku
                        break

            if sku in prices:

                # HACK: for mirrors, we want to update the price so that
                #       it also includes the dresser price
                if 'dresser' in product.title.lower() and sku.endswith('M'):
                    dresser_sku = sku[:-1]
                    dresser_sku += 'D'
                    dresser_price = parse_price(prices[dresser_sku])
                    mirror_price = parse_price(prices[sku])

                    price = calculate_price(dresser_price + mirror_price)
                else:
                    price = calculate_price(prices[sku])

                # UPDATE this thing
                # float comparison because variant.price is a str
                if float(variant.price) != float(price):

                    if float(variant.price) > float(price):
                        print "FUCK:", price, variant.price, sku, product.title

                    # update the price
                    old_price = variant.price
                    variant.price = price

                    # update the SKU, to make future pricing easier
                    if variant.sku != sku:
                        print "update SKU: %s -> %s" % (variant.sku, sku)
                        variant.sku = sku

                    print product.title, sku, old_price, price
                    variant.save()
                    num_variants += 1
                    product_updated = True
            else:
                missing_prices[product.title].append(sku)

        if product_updated:
            add_tag(product, "MAP")
            products_updated += 1

print "updated variants:", num_variants
print "updated products:", products_updated
sys.exit(0)

missing = 0
with open('missing_prices.csv', 'w') as f:
    for name in sorted(missing_prices.keys()):
        for sku in sorted(missing_prices[name]):
            f.write("%s,%s\n" % (name, sku))
            missing += 1

print "wrote %d missing SKUs to missing_prices.csv" % missing
