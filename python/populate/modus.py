import json
from urllib2 import urlopen
import sys
from pprint import pprint

from dove.product import Product
from dove import categories


# TODO setup with argparse
infile = sys.argv[1]
with open(infile, 'r') as f:
    data = json.load(f)


def extract_style(s):
    parts = s.split(' ')
    if 'St.' in parts:
        return ''.join(parts[0:2])
    elif 'II' in parts:
        return ' '.join(parts[0:2])
    else:
        return parts[0]
ok = False # TODO remove
for category_name in sorted(data.keys()):

    cat_name = category_name
    if category_name == 'Occasional':
        cat_name = "Living"

    category = data[category_name]
    category_image_url = category['image']
    subcategories = category['subcategories']

    for subcategory_name in sorted(subcategories.keys()):

        subcategory = subcategories[subcategory_name]
        products = subcategory['products']

        for product_name in sorted(products):

            if not ok and product_name != "Meadow Chest":
                continue
            ok = True

            print product_name
            product = products[product_name]
            options = product['options']
            style = extract_style(product_name)

            p = Product(name=product_name,
                        category=cat_name,
                        product_type=subcategory_name,
                        description=product['description'],
                        vendor='Modus',
                        style=style
                        )

            # Modus has a shit ton of redundant images, so uniquify them here
            images = []
            for url in product['images']:
                # download the image
                img_data = urlopen(url).read()
                if img_data not in images:
                    # only add it if we haven't seen it before
                    images.append(img_data)
                    p.add_image_url(url)

            if options:
                # create variants
                for option_name in sorted(options.keys()):
                    option = options[option_name]

                    kwargs = {
                        'sku': option['sku'],
                        'price': option['price'],
                        'weight': float(option['weight'].replace(' lbs', '')),
                        'dimensions': option['dimensions'],
                        'size': None,
                        'color': None,
                        'feature': None,
                    }

                    # figure out what type of option this is
                    if ' Bed' in product_name or 'Headboard' in product_name:
                        # these are sizes
                        kwargs['size'] = option_name
                    elif 'Height' in option_name:
                        kwargs['feature'] = option_name
                    else:
                        # these are colors
                        kwargs['color'] = option_name

                    p.add_variant(**kwargs)
            else:
                # create a single variant
                p.add_variant(size=None,
                              sku=product['sku'],
                              price=0,
                              weight=float(product['weight'].replace(' lbs', '')),
                              dimensions=product['dimensions'],
                              )

            p.upload()
