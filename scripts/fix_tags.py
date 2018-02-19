import shopify

from dove import categories, shopify_config
shopify_config.setup()


filter_args = {
    'vendor': 'Modus',
}
query_limit = 250

num_products = shopify.Product.count(**filter_args)
print num_products
# max 250 items per query, so need to do it by pages
for page in xrange(1, (num_products/query_limit)+2):
    products = shopify.Product.find(limit=query_limit, page=page,
                                    fields=['id', 'title', 'tags'],
                                    **filter_args)
    for product in products:

        # figure out the collection from the title
        t = product.title
        parts = t.split(' ')

        c = parts[0]
        maybe = parts[1]

        if c == 'St.':
            c += maybe
        elif maybe == 'II':
            c += ' ' + maybe

        # this is a comma separated string
        tags = product.tags
        tags += ', style:%s' % c
        product.tags = tags
        print t, '-->', tags
        product.save()
