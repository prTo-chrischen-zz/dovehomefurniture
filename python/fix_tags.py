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
        tags = product.tags
        corrected_tags = []
        for tag in tags.split(','):
            corrected = categories.resolve(tag.strip()).lower()
            corrected_tags.append(corrected)
        corrected_tags_str = ','.join(corrected_tags)
        print product.id, ':', tags, '->', corrected_tags_str
        product.tags = corrected_tags_str
        product.save()
