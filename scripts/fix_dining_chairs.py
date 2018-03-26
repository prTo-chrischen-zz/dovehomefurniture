import shopify

from dove import categories, shopify_config
shopify_config.setup()


filter_args = {
    'product_type': 'Chair',
    'tags': 'dining'
}
query_limit = 250

num_products = shopify.Product.count(**filter_args)
print num_products
# max 250 items per query, so need to do it by pages
for page in xrange(1, (num_products/query_limit)+2):
    products = shopify.Product.find(limit=query_limit, page=page,
                                    fields=['id', 'title', 'tags', 'product_type'],
                                    **filter_args)
    for product in products:

        tags = [i.strip() for i in product.tags.split(',')]
        product.title = product.title.replace(" Chair", " Dining Chair")
        print product.title
        if 'subcategory:Chairs' in tags:
            tags.remove('subcategory:Chairs')
            new_tags = ', '.join(tags)
            product.tags = tags
        product.product_type = "Dining Chair"
        product.save()
