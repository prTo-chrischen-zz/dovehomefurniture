import csv
import shopify
import math
import sys
import time
from collections import defaultdict
from pprint import pprint


from dove import categories, shopify_config
shopify_config.setup()

def adjust_price(p, multiplier=0.75):
    # NOTE: shopify gives prices as unicode strings
    d = int(float(p)*multiplier)

    # round to nearest 9
    return (int(math.ceil(d / 10.0)) * 10) - 1

#vendors = ('Ashley', 'Furniture of America')
vendors = ('Furniture of America',)
query_limit = 250

for vendor in vendors:
    filter_args = {'vendor': vendor}

    num_products = shopify.Product.count(**filter_args)
    # max 250 items per query, so need to do it by pages
    for page in xrange(1, ((num_products-1)/query_limit)+2):
        products = shopify.Product.find(limit=query_limit, page=page,
                                        fields=['id', 'title', 'vendor', 'price',
                                                'variants', 'product_type', 'tags'],
                                        **filter_args)
        for product in products:

            print product.title

            for variant in product.variants:

                p = variant.price
                new_p = adjust_price(p)

                print ' %s  %s -> %s' % (variant.id, p, new_p)
                variant.price = new_p

                while True:
                    try:
                        variant.save()
                        break
                    except Exception as e:
                        print e
                        print "waiting 3 secs..."
                        time.sleep(3)
                        continue
