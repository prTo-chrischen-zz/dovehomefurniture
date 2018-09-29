import csv
import shopify
import math
import os
import sys
import time
from collections import defaultdict
from pprint import pprint


from dove import categories, shopify_config
shopify_config.setup()

# load the price data
prices = {}
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
margin_file = os.path.join(root, 'resources', 'ashley', 'margins.csv')
with open(margin_file, 'r') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        subcat = row['Subcategory'].strip()
        margin = row['Margin'].strip()

        if not subcat:
            continue

        if not margin:
            margin = '50%'

        m = float(margin.strip('%'))/100.0
        if m == 1:
            # prices are already at 100% margin
            continue
        elif m > 1:
            print "ERROR: margin value > 1 '%s'" % margin
            sys.exit(0)

        # (current price in shopify) = (1+m)*(original price)
        # and our objective is to revert to 2*original (ie. 100% margin [m==1])
        # so calculate a multiplier on the current price that will get
        # us to 2*(original price)

        # 2*(original) = 2*(current / (1+m))
        # hence (multiplier on current price) = 2 / (1+m)

        multiplier = 2.0 / (1+m)

        print subcat, multiplier

        # get the collection ID for this subcategory
        cols = shopify.SmartCollection.find(fields=['title', 'id'], title=subcat)
        if len(cols) == 0:
            print "ERROR: failed to find collection '%s'" % (subcat)
            sys.exit(1)
        elif len(cols) > 1:
            cols = [i for i in cols if i.title == subcat]
            if len(cols) > 1:
                print "ERROR: more than one collection found for '%s'" % (subcat)
                print cols
                sys.exit(1)

        cid = cols[0].id

        prices[cid] = multiplier


def adjust_price(p, multiplier=0.75):
    # NOTE: shopify gives prices as unicode strings
    d = int(float(p)*multiplier)

    # round to nearest 9
    return (int(math.ceil(d / 10.0)) * 10) - 1

vendor = 'Ashley'
query_limit = 250

for cid, multiplier in prices.iteritems():
    filter_args = {'collection_id': cid, 'vendor': vendor}

    num_products = shopify.Product.count(**filter_args)
    # max 250 items per query, so need to do it by pages
    for page in xrange(1, ((num_products-1)/query_limit)+2):

        while True:
            try:
                products = shopify.Product.find(limit=query_limit, page=page,
                                                fields=['title', 'variants', 'product_type'],
                                                **filter_args)
                break
            except Exception as e:
                print "ERROR:", e
                print "waiting 3 secs..."
                time.sleep(3)
                continue

        for product in products:

            print product.title

            for variant in product.variants:

                p = variant.price
                new_p = adjust_price(p, multiplier=multiplier)

                print ' %s  %s -> %s (%s)' % (variant.id, p, new_p, multiplier)

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
