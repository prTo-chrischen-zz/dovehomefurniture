
import csv
import os
import re
import sys

from dove.product import Product
from dove import categories

data = None
with open(sys.argv[1], 'r') as f:
    reader = csv.DictReader(f, delimiter=',')
    data = [row for row in reader]

prefix_regex = re.compile(r'^(CM\d{4})')
def prefix(sku):
    m = prefix_regex.match(sku)
    if not m:
        raise ValueError("Couldn't parse out prefix for '%s'" % sku)
    return m.group(1)

# We want to collapse all the beds into a single product, with each size
# (King, Queen, etc.) as a variant within that product. The data has each of
# these sizes as a separate row, with its own SKU, and potentially only one of
# them actually has an image

# SKU prefix -> Product object
products = {}
vendor = "Furniture of America"

header = data[0]
for row in data[1:]:
    pname = row['Name'].strip()
    if not pname:
        print " [ERROR] missing name: ", sku
        continue

    sku = row["Item"]
    category = row["Categories"]
    product_type = row["Sub-Categories"]
    description = row["Summary"]
    size = row["Size"]
    weight = row["Shipping Weight (LB)"]
    color = row["Color"]
    image = row["Reference Image"].strip()
    dimensions = row["Product Dimension (Inch)"]
    materials = row["Material"].strip()

    if size == '#N/A':
        # try and parse it out in the short description
        size = row['Short Description'].replace('Bed', '').split(' ')[0]
        print " [WARNING] deriving size:", sku, size
    elif size == '0':
        size = None

    # build the name
    name = "%s %s %s" % (pname, row['Style'],
                         categories.resolve(product_type))
    pkey = name

    if pkey in products:
        product = products[pkey]
    else:
        product = Product(name, category, product_type, description, vendor)
        products[pkey] = product

    # add a variant
    product.add_variant(sku, size, weight=weight, dimensions=dimensions)

    if color:
        product.add_color(color)

    if image:
        product.add_image(image)

    if materials:
        materials = materials.replace('& Others', '')
        for mat in materials.split(','):
            product.add_tag("material:%s" % mat.strip())

from pprint import pprint
for pkey, product in products.iteritems():
    print '==', product.name
    pprint(product.data())
