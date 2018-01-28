import shopify


api_key = '4a1491f99a78af6781acb755fa63a2f6'
password = '8dfd0d4d473d260791c54aa0d9719cec'
admin_url = 'https://%s:%s@dove-home-furniture.myshopify.com/admin' % (api_key, password)


def setup():
    shopify.ShopifyResource.set_site(admin_url)
    return shopify.Shop.current()
