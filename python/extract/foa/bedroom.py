
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

prefix_regex = re.compile(r'^(CM\d{4})')
def derive_bed_pkey(sku):
    m = prefix_regex.match(sku)
    if not m:
        raise ValueError("Couldn't parse out prefix for '%s'" % sku)
    return m.group(1) + '-BED'

vendor = "Furniture of America"

header = data[0]
for row in data[1:]:
    style = row['Name'].strip().upper()
    if not style:
        print " [ERROR] missing style: ", sku
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

    # --- begin bullshit specific to beds
    # bed products are a pain in the dick, because name will be the same for
    # both the featured and feature-less versions of the same bed
    # eg.   "EMMALINE Traditional Bed, Wooden H/B"
    #    vs "EMMALINE Traditional Bed"
    feature = None
    try:
        feature = row['Feature'].strip()
    except KeyError:
        pass
    else:
        if 'w/' in feature:
            # only want the feature itself, trim shit
            feature = feature[feature.find('w/'):]
        elif ',' in feature:
            feature = feature[feature.find(', ')+2:]
        elif feature:
            raise ValueError("WTF feature is '%s'" % feature)
        else:
            feature = None
    # --- end bed bullshit

    if size == '#N/A':
        # try and parse it out in the short description
        size = row['Short Description'].replace('Bed', '').split(' ')[0]
        print " [WARNING] deriving size:", sku, size
    elif size == '0':
        size = None

    image_path = os.path.join("f:/tmp/upload", image)
    if not os.path.isfile(image_path):
        #print " [ERROR] missing image:", image_path
        image_path = None

    # build the name
    name = "%s %s %s" % (style, row['Style'],
                         categories.resolve(product_type))
    pkey = name

    product = doveprod.get_or_make_product(
                product_key=pkey, name=name, category=category,
                product_type=product_type, description=description,
                vendor=vendor, style=style)

    # each row is a size; no prices in FoA data
    try:
        product.add_variant(size, sku, price=0, weight=weight,
                            dimensions=dimensions, color=color, image=image_path,
                            feature=feature)
    except doveprod.VariantError as e:
        print "ERROR:", str(e)
        continue

    # typically all products have the same description
    if description and not product.description:
        product.description = description

    if materials:
        materials = materials.replace('& Others', '')
        for mat in materials.split(','):
            product.add_tag('material', mat.strip())

    if feature and feature.endswith('Drawers'):
        product.add_tag('feature', 'Storage')

for pkey, product in doveprod.get_products():
    print pkey
    product.upload()
