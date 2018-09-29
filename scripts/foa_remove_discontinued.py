import csv
import shopify
import math
import sys
from collections import defaultdict


# load the price data
discontinued = set()
with open(sys.argv[1], 'r') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        sku = row["Item"]
        discontinued.add(sku)


from dove import categories, shopify_config
shopify_config.setup()

filter_args = {'vendor': 'Furniture of America'}
query_limit = 250

sku_suffixes = [
    '-BED',
    '-TABLE',
    '-SECTIONAL',
    '-PK',
]

variants_removed = 0
products_removed = []

num_products = shopify.Product.count(**filter_args)
# max 250 items per query, so need to do it by pages
for page in xrange(1, ((num_products-1)/query_limit)+2):
    products = shopify.Product.find(limit=query_limit, page=page,
                                    fields=['id', 'vendor', 'title', 'variants', 'product_type'],
                                    **filter_args)

    for product in products:

        num_removed = 0

        for variant in product.variants:
            sku = variant.sku

            if sku in discontinued:
                print "MATCH:", product.title, sku
                # note: destroy immediately removes the variant from shopify
                variant.destroy()
                num_removed += 1
            else:
                # check to see if it has a suffixed version
                for suffix in sku_suffixes:
                    s = '%s%s' % (sku, suffix)
                    if s in discontinued:
                        print "[suffix]", product.title, s
                        # note: destroy immediately removes the variant from shopify
                        variant.destroy()
                        num_removed += 1
                        break

        destroy = False

        if num_removed and product.product_type == 'Dresser':
            # if any dresser variants get removed, kill the whole thing
            destroy = True
        elif num_removed == len(product.variants):
            # if we destroyed all the variants, delete the product
            destroy = True

        if not destroy and num_removed:
            # keep track of individual variant removals that didn't lead to
            # product removals
            variants_removed += num_removed

        if destroy:
            products_removed.append(product.title)
            # NOTE: this immediately destroys the product on shopify
            print "DELETE PRODUCT:", product.title
            product.destroy()

print "removed %d variants, %d products" % (variants_removed, len(products_removed))
