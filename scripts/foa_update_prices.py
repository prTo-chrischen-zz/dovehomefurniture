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

filter_args = {'vendor': 'Furniture of America'}
query_limit = 250

num_variants = 0
missing_prices = defaultdict(list)

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

num_products = shopify.Product.count(**filter_args)
# max 250 items per query, so need to do it by pages
for page in xrange(1, ((num_products-1)/query_limit)+2):
    products = shopify.Product.find(limit=query_limit, page=page,
                                    fields=['id', 'vendor', 'title', 'variants'],
                                    **filter_args)

    for product in products:

        for variant in product.variants:
            # every variant should have a SKU
            sku = variant.sku
            num_variants += 1

            if sku not in prices:
                # check to see if it has a suffix-less version
                for suffix in sku_suffixes:
                    if sku.endswith(suffix):
                        sku = sku[:-len(suffix)]
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

                # UPDATE price
                old_price = variant.price
                variant.price = price

                if variant.sku != sku:
                    print "update SKU: %s -> %s" % (variant.sku, sku)
                    # UPDATE SKU
                    variant.sku = sku

                print product.title, sku, old_price, price
                variant.save()
            else:
                missing_prices[product.title].append(sku)

print "total variants:", num_variants

missing = 0
with open('missing_prices.csv', 'w') as f:
    for name in sorted(missing_prices.keys()):
        for sku in sorted(missing_prices[name]):
            f.write("%s,%s\n" % (name, sku))
            missing += 1

print "wrote %d missing SKUs to missing_prices.csv" % missing
