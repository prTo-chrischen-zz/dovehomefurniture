import shopify

from dove import categories, shopify_config
shopify_config.setup()


for category, cat_data in categories._categories.iteritems():
    for subcategory in sorted(cat_data.keys()):
        results = shopify.SmartCollection.find(title=subcategory, limit=1)
        print subcategory,
        if results:
            c = results[0]
            c.sort_order = "alpha-asc"
            c.save()
            print "FIXED"
        else:
            print "NOT FOUND"
