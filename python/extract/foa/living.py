
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
    if not style:
        error("missing style: %s" % (sku))
        continue

    category = row["Categories"]
    product_type = row["Product Type"]
    description = row["Summary"]
    weight = row["Shipping Weight (LB)"]
    color = row["Color"]
    image = row["Reference Image"].strip()
    dimensions = row["Product Dimension (Inch)"]
    materials = row["Material"].strip()
    size = row["Size"].strip()
    feature = row["Feature"].strip()

    if size in ('#N/A', '0'):
        size = None

    image_path = os.path.join("/Users/dcheng/Desktop/upload", image)
    if not os.path.isfile(image_path):
        print " [ERROR] missing image:", image_path
        image_path = None

    # build the name
    name = "%s %s %s" % (style, row['Style'], product_type)

    try:
        product = doveprod.get_or_make_product(
                product_key=name, name=name, category=category,
                product_type=product_type, description=description,
                vendor=vendor, style=style)
    except categories.InvalidProductTypeError as e:
        error("Invalid product type '%s' for %s" % (product_type, sku))
        continue

    # each row is a size; no prices in FoA data
    try:
        product.add_variant(size, sku, price=0, weight=weight,
                            dimensions=dimensions, color=color, image=image_path,
                            feature=feature)
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

sys.exit(0)
notyet = True
for pkey, product in doveprod.get_products():
    #if notyet and pkey != 'PRISMO II Cottage Bunk Bed':
    #    continue
    #notyet = False
    print pkey
    product.upload()
