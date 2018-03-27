import csv
import os
import re
import sys
from pprint import pprint

from dove import product as doveprod
from dove import categories

data = None
with open(sys.argv[1], 'r') as f:
    reader = csv.DictReader(f, delimiter=',')
    data = [row for row in reader]

def error(msg):
    print "[ERROR]", msg

vendor = "Furniture of America"


header = data[0]
for row in data[1:]:
    sku = row["Item"]
    style = row['Name'].strip().upper()
    category = row["Categories"]
    product_type = row["Product Type"]
    description = row["Summary"]
    weight = row["Shipping Weight (LB)"]
    color = row["Color"]
    image = row["Reference Image"].strip()
    dimensions = row["Product Dimension (Inch)"]
    materials = row["Material"].strip()
    size = row["Size"].strip()
    display_name = row["Display Name"].strip()
    feature = row["Feature"].strip().replace('W/', 'w/')
    tag = row["Filter Tag"].replace('W/', 'w/')

    name = ' '.join([style, row['Style'],
                     (display_name if display_name else product_type)])

    if category == 'Office':
        category = 'Home Office'

    if size == '#N/A' or size == '0' or not size:
        size = None

    image_path = None
    if image:
        path = os.path.join("f:/tmp/orig", image)
        if os.path.isfile(path):
            image_path = path
    if not image_path:
        error("no image for %s" % sku)
        continue

    try:
        product = doveprod.get_or_make_product(
            product_key=name, name=name, category=category,
            product_type=product_type, description=description,
            vendor=vendor, style=style)
    except categories.InvalidProductTypeError as e:
        error("Invalid product type '%s' for %s" % (product_type, sku))
        continue

    try:
        product.add_variant(size, sku, price=0, weight=weight,
                            dimensions=dimensions, color=color, image=image_path,
                            feature=feature)
    except doveprod.VariantError as e:
        error(str(e))

    if tag:
        product.add_tag('feature', tag)

for pkey, product in doveprod.get_products():
    print pkey
    product.upload()
