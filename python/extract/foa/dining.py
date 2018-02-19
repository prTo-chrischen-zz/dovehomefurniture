
import csv
import os
import sys
from pprint import pprint

from dove import product as doveprod
from dove import categories

data = None
with open(sys.argv[1], 'r') as f:
    reader = csv.DictReader(f, delimiter=',')
    data = [row for row in reader]

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
    subcategory = row["Sub-Categories"]
    description = row["Summary"]
    weight = row["Shipping Weight (LB)"]
    color = row["Color"]
    image = row["Reference Image"].strip()
    dimensions = row["Product Dimension (Inch)"]
    materials = row["Material"].strip()
    feature = row['Tag #1'].strip()

    if product_type == 'Dining Misc.':
        product_type = row['Short Description'].split(',')[0]

    size = row["Size"]
    if size in ('#N/A', '0'):
        size = None

    image_path = os.path.join("f:/tmp/upload", image)
    if not os.path.isfile(image_path):
        #print " [ERROR] missing image:", image_path
        image_path = None

    # build the name
    name = "%s %s %s" % (style, row['Style'],
                         categories.resolve(product_type))
    # FoA bullshit inconsistent data
    if 'Mid-Century' in name:
        name = name.replace('Mid-Century', 'Midcentury')
    pkey = name

    product = doveprod.get_or_make_product(
                product_key=pkey, name=name, category=category,
                product_type=product_type, description=description,
                vendor=vendor, style=style, subcategory=subcategory)

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

for pkey, product in doveprod.get_products():
    print pkey
    product.upload()