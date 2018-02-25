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


# substrings that, if found, will cause an item to be skipped
ignores = (
    'back cushion',
    'bracket',
    'corner wedge',
    ' footboard',
    ' ftbd',
    'panel rails',
    'poster rails',
    ' posts',
    'photo frame',
    'quilt set',
    'sofa/love sec/end tbls', # bullshit outdoor crap
    'vase',
    'w/UPH Stools (3/CN)',

)

# trivial mappings that don't require code
cat_map = {
    'Medium Rug': ('Living', 'Rug'),
    'Sofa': ('Living', 'Sofa'),
}

# beds are made up of a Headboard, Footboard, and Rails
# TODO does something in the XML tell us this?

class SkipExc(Exception):
    pass

def breakdown(to_split, by_s):
    parts = to_split.split(by_s)
    return (parts[0].strip(), parts[1].strip())

def figure_out(s, out_data=None):
    """Figure out the category/type of s"""
    try:
        return cat_map[s]
    except KeyError:
        pass

    low_s = s.lower()
    for ignore in ignores:
        if ignore in low_s:
            raise SkipExc(s)

    # (category, product_type)
    ret = [None, None]
    def setvals(c, p):
        ret[0] = c
        ret[1] = p

    tags = []
    feature = None
    size = None
    name_prefix = None
    name_suffix = None

    if "Loveseat" in s:
        # tease out the size/features
        pre, post = breakdown(s, "Loveseat")
        if 'cushion' in post.lower() and '/' not in post:
            raise SkipExc(s)
        setvals("Living", "Loveseat")
    elif "Home Office" in s:
        if 'Desk Chair' in s:
            if '(2/CN)' in s: name_suffix = "x2"
            setvals("Office", "Office Chair")
    elif "Dining" in s:
        if "Chair" in s:
            if "UPH" in s: tags.append(('feature', 'Upholstered'))
            if 'Arm' in s: feature = 'Arm'
            if 'Side' in s: feature = 'Side'
            if '(2/CN)' in s: name_suffix = "x2"
            setvals("Dining", "Chair")
    elif "Recliner" in s:
        if 'LAF' in s or 'RAF' in s:
            raise SkipExc(s)
        if 'Armless' in s: tags.append(('feature', 'Armless'))
        if 'Glider' in s:
            name_prefix = "Glider"
            tags.append(('feature', 'Glider'))
        if 'Rocker' in s:
            name_prefix = "Rocker"
            tags.append(('feature', 'Rocker'))
        if 'High Leg' in s: tags.append(('feature', 'High Leg'))
        if 'Low Leg' in s: tags.append(('feature', 'Low Leg'))
        if 'Power' in s:
            feature = "Power"
            tags.append(('feature', 'Power'))
        if 'Power Lift' in s: tags.append(('feature', 'Power Lift'))
        if 'Swivel' in s: tags.append(('feature', 'Swivel'))
        if 'Wide' in s: tags.append(('feature', 'Wide'))
        if 'Zero Wall' in s: tags.append(('feature', 'Zero Wall'))
        setvals("Living", "Recliner")
    elif "Headboard" in s:
        if 'Queen/Full' in s:  size = ['Queen', 'Full']
        elif 'Queen/King' in s: size = ['Queen', 'King']
        elif 'Twin/Full' in s: size = ['Twin', 'Full']
        elif 'KG/CK' in s or 'K/CK' in s or 'King/Cal King' in s:
            size = ['King', 'C. King']
        elif 'Twin' in s: size = 'Twin'
        elif 'Full' in s: size = 'Full'
        elif 'Queen' in s: size = 'Queen'
        elif 'King' in s: size = 'King'
        if 'UPH' in s or 'Upholstered' in s: tags.append(('feature', 'Upholstered'))
        for pre in ('Bookcase', 'Panel', 'Poster', 'Sleigh', 'Storage', 'Louvered', 'Slat'):
            if pre in s:
                name_prefix = pre
                tags.append(('feature', pre))
                break
        setvals("Bedroom", "Bed")
    elif "Media Chest" in s:
        pre, post = breakdown(s, "Media Chest")
        if 'w/' in post:
            tags.append(('feature', post.replace('w/', '')))
        setvals("Bedroom", "Media Chest")
    elif "Night Stand" in s:
        pre, post = breakdown(s, "Night Stand")
        if pre:
            tags.append(('feature', pre))
        if post:
            raise TypeError(s)
        setvals("Bedroom", "Nightstand")
    elif "Chair" in s:
        pre, post = breakdown(s, "Chair")
        if pre:
            tags.append(('feature', pre))
        if post:
            feature = post
        setvals("Living", "Chair")
    elif "Stool" in s and "Stools" not in s:
        pre, post = breakdown(s, "Stool")
        if 'UPH' in pre:
            pre = pre.replace('UPH', '').strip()
            tags.append(('feature', 'Upholstered'))
        if 'Upholstered' in pre:
            pre = pre.replace('Upholstered', '').strip()
            tags.append(('feature', 'Upholstered'))
        if pre:  size = pre
        setvals("Dining", "Stool")
    elif "Wall Art" in s:
        if   '2/CN' in s: name_suffix = "x2"
        elif '3/CN' in s: name_suffix = "x3"
        elif '4/CN' in s: name_suffix = "x4"
        elif '5/CN' in s: name_suffix = "x5"
        setvals("Accessories", "Wall Decor")
    elif "Cocktail Table" in s:
        pre, post = breakdown(s, "Cocktail Table")
        if "with Storage" in post:
            tags.append(('feature', 'Storage'))
        if pre: tags.append(('feature', pre))
        setvals("Living", "Coffee Table")
    elif "Sofa" in s:
        if "Table" in s and 'Drop Down Table' not in s:
            if '/CN' in s:
                raise SkipExc(s)
            if 'Console' in s:
                tags.append(('feature', 'Console'))
                setvals("Living", "Console Table")
            else:
                setvals("Living", "Sofa Table")
        else:
            if "LAF " in s or "RAF " in s: raise SkipExc(s)
            if "Armless" in s: tags.append(('feature', "Armless"))
            if "Reclining" in s or "REC" in s:
                tags.append(('feature', 'Reclining'))
            if "Power" in s:
                tags.append(('feature', "Power"))
                feature = "Power"
            if "Sofa Chaise" in s: tags.append(('feature', "Chaise"))
            if "Sleeper" in s:
                tags.append(('feature', "Sleeper"))
                if "Twin" in s: size = "Twin"
                elif "Full" in s: size = "Full"
                elif "Queen" in s: size = "Queen"
            setvals("Living", "Sofa")
    elif "Mirror" in s:
        if 'Floor Standing' in s: tags.append(('feature', 'Standing'))
        if 'Vanity' in s: tags.append(('feature', 'Vanity'))
        if 'Bedroom' in s:
            setvals('Bedroom', 'Mirror')
        else:
            setvals('Accessories', 'Mirror')

    if not ret[0] or not ret[1]:
        raise TypeError(s)

    if tags: out_data['tags'] = tags
    if size: out_data['size'] = size
    if feature: out_data['feature'] = feature
    if name_suffix: out_data['name_suffix'] = name_suffix
    if name_prefix: out_data['name_prefix'] = name_prefix

    return ret

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

    additional_info = {}
    try:
        category, product_type = figure_out(pt_str, additional_info)
    except SkipExc as e:
        print "Skip:", str(e)
        continue
    except TypeError as e:
        print sku
        raise

    style = group.get("groupName")
    adjective = group.get("groupStyle")
    name_parts = [style, adjective]
    if 'name_prefix' in additional_info:
        name_parts.append(additional_info['name_prefix'])
    name_parts.append(product_type)
    if 'name_suffix' in additional_info:
        name_parts.append(additional_info['name_suffix'])
    name = " ".join(name_parts)
    print pt_str
    print "    ", name, sku, additional_info

    continue

    if 'size' in additional_info:
        if isinstance(list, additional_info['size']):
            # TODO create two variants
            pass
        else:
            # make one variant
            pass

    doveprod.get_or_make_product(
        product_key=pkey,
        name=name,)
