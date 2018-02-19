import shopify

from dove import categories, shopify_config
shopify_config.setup()


query_limit = 250

num_products = shopify.Product.count()
print num_products
# max 250 items per query, so need to do it by pages
for page in xrange(1, (num_products/query_limit)+2):
    products = shopify.Product.find(limit=query_limit, page=page,
                                    fields=['id', 'tags'])
    for product in products:
        # do some shit to it
        # example: product.vendor = "Modus"
        continue
        product.save()
