import shopify

from dove import categories, shopify_config
shopify_config.setup()


filter_args = {
    'product_type': 'Bench',
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

        tags = [i.strip() for i in product.tags.split(',')]
        if 'dining' in tags:
            print product.title
            if 'Bench' in tags and 'Dining Bench' not in tags:
                tags.remove('Bench')
                tags.insert(0, 'Dining Bench')
                new_tags = ', '.join(tags)
                product.tags = tags
                product.save()
