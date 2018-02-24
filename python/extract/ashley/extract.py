import cPickle as pickle
import sys
import xml.etree.ElementTree as ET
from pprint import pprint

import dove.product as doveprod
from dove import categories


cache_file = sys.argv[1]
with open(cache_file, 'rb') as f:
    data = pickle.load(f)

# should be groupID -> <xml Element>
groups = data['groups']
# should be sku -> <xml Element>
items = data['items']


ignore = set((

))

cat_map = {
    'Sofa': ('Sofa', 'Living'),
}

# beds are made up of a Headboard, Footboard, and Rails
# TODO does something in the XML tell us this?

def figure_out(s):
    """Figure out the category/type of s"""
    try:
        return cat_map[s]
    except KeyError:
        pass

    if "Loveseat" in s:
        # tease out the size/features
        pass


    raise TypeError(s)

for sku, item in items.iteritems():
    groupID = item.get('itemGroupCode')
    group = groups[groupID]

    if item.get("itemStatus") == "Discontinued":
        continue

    # figure out the UPC
    upc = None
    sku = None
    item_ident = item.find('itemIdentification')
    for identifier in item_ident.findall('itemIdentifier'):
        qualifier = identifier.get('itemNumberQualifier')
        if qualifier == 'UPC':
            upc = identifier.get('itemNumber')
        elif qualifier == 'SellerAssigned':
            sku = identifier.get('itemNumber')

    item_desc = item_ident.find('itemDescription')
    # have to parse this fucker to figure out wtf this thing is
    pt_str = item_desc.get('descriptionValue')

    if pt_str in ignore:
        continue

    category, product_type = figure_out(pt_str)

    continue
    doveprod.get_or_make_product(
        product_key=pkey,
        name=name,)
