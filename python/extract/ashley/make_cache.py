#!python

"""
Make a pickle cache from a bunch of Ashley XMLs, so that we don't have to
load XML (which is fucking expensive) every time.
"""

import cPickle as pickle
import sys
import xml.etree.ElementTree as ET
from pprint import pprint


# take a bunch of xml files as input
fpaths = sys.argv[1:]

# stuff to be pickled
groups = {}
items = {}
data = {'items': items, 'groups': groups}

for fpath in fpaths:
    tree = ET.parse(fpath)

    root = tree.getroot()

    item_tree = root.find('items')
    group_tree = root.find('groups')

    # build a dict for the groups, for easy access later
    # example group name: "Loughran"
    for group in group_tree:
        # example groupID: "PA300"
        groups[group.get('groupID')] = group

    for item in item_tree:
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

        # assuming that SKUs will uniquely identify an "item"
        if sku not in items:
            items[sku] = item

with open('cache.pickle', 'wb') as f:
    pickle.dump(data, f, protocol=2)