import json
import shopify

# required shop boilerplate
import shopify_config
shopify_config.setup()


# TODO setup with argparse

with open(infile, 'r') as f:
    data = json.load(f)

for category_name in sorted(data.keys()):
    category = data[category_name]
    category_image_url = category['image']
    subcategories = category['subcategories']

    category_rules = []

    for subcategory_name in sorted(subcategories.keys()):
        category_rules.append({
            'column': 'product_type',
            'relation': 'equals',
            'condition': subcategory_name
        })

        subcategory = subcategories[subcategory_name]
        products = subcategory['products']
        subcategory_image = subcategory['image']

        for product_name in sorted(products):
            print product_name
            product = products[product_name]
            options = product['options']

            p = shopify.Product()
            p.title = product_name
            p.body_html = product['description']
            p.product_type = subcategory_name
            p.images = [{'src': img_url} for img_url in product['images']]

            variants = []
            if options:
                # create variants
                for option_name in sorted(options.keys()):
                    option = options[option_name]
                    variants.append({
                        'sku': option['sku'],
                        'price': option['price'],
                        'option1': option_name,
                        'weight': float(option['weight'].replace(' lbs', '')),
                        'weight_unit': 'lb',
                        'price': option['price'],
                    })
            else:
                # create a single variant
                variants.append({
                    'sku': product['sku'],
                    'price': 0,
                    'option1': '',
                    'weight': float(product['weight'].replace(' lbs', '')),
                    'weight_unit': 'lb',
                })

            p.variants = variants
            p.save()
            if p.errors:
                print " ERROR:", p.errors.full_messages()

