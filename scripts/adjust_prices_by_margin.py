import csv
import shopify
import math
import sys
import time
from collections import defaultdict
from pprint import pprint


from dove import categories, shopify_config
shopify_config.setup()

# load the price data
prices = {}
cwd = os.path.dirname(os.path.abspath(__file__))
margin_file = os.path.join(cwd, 'resources', 'ashley', 'margins.csv')
with open(margin_file, 'r') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        subcat = row['Subcategory'].strip()
        margin = row['Margin'].strip()

        if not subcat:
            continue

        if not margin:
            margin = '50%'

        if margin:
            m = float(margin.strip('%'))/100.0
            if m == 1:
                # prices are already at 100% margin
                continue
            elif m > 1:
                print "ERROR: margin value > 1 '%s'" % margin
                sys.exit(0)
            # this is the multiplier on the base price that we want (1 + margin)
            desired_p = 1 + m

            # since everything is at 2x base right now, the actual multiplier
            # is (1+margin)/2
            # ie. 60% margin -> (1+.6)/2 = 0.8
            multiplier = desired_p/2.0
        else:
            # otherwise, set to 50% margin
            multiplier = 0.75

        print subcat

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
        print multiplier


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
