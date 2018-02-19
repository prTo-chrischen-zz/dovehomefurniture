
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
    style = row['Name'].strip().upper()
    if not style:
        error("missing style: %s" % (sku))
        continue

    sku = row["Item"]
    category = row["Categories"]
    subcategory = row["Sub-Categories"]
    product_type = row["Sub-Categories"]
    description = row["Summary"]
    weight = row["Shipping Weight (LB)"]
    color = row["Color"]
    image = row["Reference Image"].strip()
    dimensions = row["Product Dimension (Inch)"]
    materials = row["Material"].strip()
    size = row["Size"].strip()

    if product_type == 'Youth Misc.':
        product_type = row['Short Description'].split(',')[0]

    if size == '#N/A':
        # try and parse it out in the short description
        size = row['Short Description'].replace('Bed', '').split(' ')[0]
        print " [WARNING] deriving size:", sku, size
    elif size == '0':
        size = None
    elif "/" in size:
        # bunk beds are annoying and have weird size strings
        size = size.split(' ')[0]


    image_path = os.path.join("f:/tmp/upload", image)
    if not os.path.isfile(image_path):
        #print " [ERROR] missing image:", image_path
        image_path = None

    # build the name
    name = "%s %s %s" % (style, row['Style'], product_type)

    try:
        product = doveprod.get_or_make_product(
                product_key=name, name=name, category=category,
                product_type=product_type, description=description,
                vendor=vendor, style=style, subcategory=subcategory)
    except categories.InvalidProductTypeError as e:
        error("Invalid product type '%s' for %s" % (product_type, sku))
        continue

    # fuck FOA's shitty data
    product.enforce_bed_sizing = False

    # each row is a size; no prices in FoA data
    try:
        product.add_variant(size, sku, price=0, weight=weight,
                            dimensions=dimensions, color=color, image=image_path)
    except doveprod.VariantError as e:
        error(str(e))
        continue

    # typically all products have the same description
    if description and not product.description:
        product.description = description

    if materials:
        materials = materials.replace('& Others', '')
        for mat in materials.split(','):
            product.add_tag('material', mat.strip())

for pkey, product in doveprod.get_products():
    pprint(product.data())
    continue
    product.upload()