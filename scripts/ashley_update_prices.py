import csv
import shopify
import math
import sys
from collections import defaultdict


from dove import categories, shopify_config
shopify_config.setup()

filter_args = {'vendor': 'Ashley'}
query_limit = 250

num_variants = 0

def calculate_price(price_str):
    p = price_str.replace('$', '')
    p = p.replace(',', '')
    d = int(float(p) * 2)
    # round to nearest 9
    return (int(math.ceil(d / 10.0)) * 10) - 1


product_types = [
    'Chest',
    'Dresser',
    'Media Chest',
    'Nightstand'
]


for product_type in product_types:

    filter_args['product_type'] = product_type

    num_products = shopify.Product.count(**filter_args)
    # max 250 items per query, so need to do it by pages
    for page in xrange(1, ((num_products-1)/query_limit)+2):
        products = shopify.Product.find(limit=query_limit, page=page,
                                        fields=['id', 'vendor', 'title', 'variants'],
                                        **filter_args)
        for product in products:
            print product.title
            for variant in product.variants:
                sku = variant.sku
                num_variants += 1

                # Apply a 15.5% shipping premium
                # ...but since the prices were already doubled in the import
                # script, just do 7.75%

                p = float(variant.price)
                # round to the nearest 9
                price = int(math.ceil(p*1.0775 / 10.0)) * 10 - 1

                print sku, p, '-->', price
                variant.price = price
                variant.save()

print "total variants:", num_variants
