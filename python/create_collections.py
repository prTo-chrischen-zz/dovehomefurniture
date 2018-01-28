import json
import shopify
import sys

infile = sys.argv[1]

api_key = '4a1491f99a78af6781acb755fa63a2f6'
password = '8dfd0d4d473d260791c54aa0d9719cec'
admin_url = 'https://%s:%s@dove-home-furniture.myshopify.com/admin' % (api_key, password)

shopify.ShopifyResource.set_site(admin_url)

shop = shopify.Shop.current()

def create_collection(title, image_url, rules):
    collection = shopify.SmartCollection()
    collection.title = title
    collection.image = {'src': image_url}
    collection.rules = rules
    collection.save()
    if collection.errors:
        print "Error processing collection:", title, collection.errors.full_messages()
    return collection

with open(infile, 'r') as f:
    data = json.load(f)

for category_name in sorted(data.keys()):
    category = data[category_name]
    category_image_url = category['image']
    subcategories = category['subcategories']

    # for creating the category collections, after subcategories have been parsed
    category_rules = []

    for subcategory_name in sorted(subcategories.keys()):
        category_rules.append({
            'column': 'type',
            'relation': 'equals',
            'condition': subcategory_name
        })

        subcategory = subcategories[subcategory_name]
        subcategory_image = subcategory['image']

        subcategory_rules = []
        subcategory_rules.append({
            'column': 'type',
            'relation': 'equals',
            'condition': subcategory_name
        })

        # create subcategory collection
        print "Creating subcategory collection ", subcategory_name
        create_collection(subcategory_name, subcategory_image, subcategory_rules)

    # creates the category collections (bedroom, living, etc) with rules that product type matches each subcategory (beds, nightstands, etc)
    print "Creating root category collection ", category_name
    create_collection(category_name, category_image_url, category_rules)
