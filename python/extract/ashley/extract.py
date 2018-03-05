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
    'w/UMB OPT',
    'Replaced by W635-134 Pier', # Old category they're too lazy to remove
    "HYBRID UNIT", # Store display units for mattress cross sections
    'Rails', # We only want Headboards to identify beds
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
        if ignore.lower() in low_s:
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
    # Because some fucking idiot decided to put one type in all caps
    elif "LOVESEAT" in s:
        # tease out the size/features
        pre, post = breakdown(s, "LOVESEAT")
        if 'cushion' in post.lower() and '/' not in post:
            raise SkipExc(s)
        setvals("Living", "Loveseat")
    elif "Home Office" in s:
        if 'Desk Chair' in s:
            if '(2/CN)' in s: name_suffix = "x2"
            setvals("Office", "Office Chair")
        if 'Cabinet' in s:
            setvals("Office", "Cabinet")
        if 'Table' in s:
            setvals("Office", "Corner Table")
    elif "Dining" in s or 'DRM' in s:
        if "Chair" in s:
            if "UPH" in s: tags.append(('feature', 'Upholstered'))
            if 'Arm' in s: feature = 'Arm'
            if 'Side' in s: feature = 'Side'
            if '(2/CN)' in s: name_suffix = "x2"
            setvals("Dining", "Chair")
        elif "Table" in s or 'TBL' in s:
            if "Dining Table" in s:
                if "Rectangular" in s: tags.append(('feature', 'Rectangular'))
            elif "Dining Room" in s:
                if "Top" in s: raise SkipExc(s)
                if "6/CN" in s: name_suffix = "(6 Piece)"
                if "7/CN" in s: name_suffix = "(7 Piece)"
                if "EXT" in s: tags.append(('feature', 'Extendable'))
                if "RECT" in s: tags.append(('feature', 'Rectangular'))
                if "Rectangular" in s: tags.append(('feature', 'Rectangular'))
                if "Round" in s: tags.append(('feature', 'Round'))
            setvals("Dining", "Table")
        elif 'Bench' in s:
            if 'UPH' in s: tags.append(('feature', 'Upholstered'))
            setvals("Dining", "Bench")
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
    elif "Headboard" in s or "HDBD" in s:
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
        for pre in ('Bookcase', 'Panel', 'Poster', 'Sleigh', 'Storage', 'Louvered', 'Slat', 'Canopy', 'Mansion', 'Metal'):
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
    elif "Night Stand" in s or "Night Table" in s:
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
    elif "Rug" in s:
        if 'Large' in s: size = 'Large'
        elif 'Medium' in s: size = 'Medium'
        # There's also a Rug Swatch Display Unit, which neither Ashley nor competitors have. Leaving it out
        setvals('Accessories', 'Rug')
    # This is for sectionals, we'll only be dealing with the Wedges as a placeholder for David-
    # half and corner wedges not included!
    elif "Wedge" in s and "Corner Wedge" not in s and "Half Wedge" not in s:
        if "Oversized" in s: size = Oversized
        setvals('Living', 'Sectional')
    # Not a Sofa Sleeper otherwise would have been caught above
    # Sectional Sleeper
    elif "Sleeper" in s and "Armless" in s:
        if "Full" in s: size = "Full"
        setvals('Living', 'Sectional')
    # Putting this in Accessories for now, since technically not 'furniture'
    elif "Comforter" in s:
        if "King" in s: size = "King"
        if "Queen" in s: size = "Queen"
        if "Full" in s: size = "Full"
        if "Twin" in s: size = "Twin"
        setvals('Accessories', 'Bedding')
    # A pier is a tower of a home entertainment center; TV goes in middle of two Piers
    elif "Pier" in s:
        if "Right" in s: tags.append(('feature', 'Right side'))
        if "Left" in s: tags.append(('feature', 'Left side'))
        if "Tall" in s: size = "Tall"
        setvals('Living', 'Pier Cabinet')
    elif "Cabinet" in s:
        if "File" in s:
            if "Lateral" in s: tags.append(('feature', 'Lateral'))
            setvals('Office', 'File Cabinet')
        elif "Display" in s: setvals('Dining', 'Display Cabinet')
        elif "Wine" in s: setvals('Dining', 'Wine Cabinet')
        elif "Accent" in s: setvals('Living', 'Cabinet')
        elif "Storage" in s:
            tags.append(('feature', 'Storage'))
            setvals('Living', 'Storage Cabinet')
    elif "Lamp" in s:
        # First, handle locations
        if "Table" in s: tags.append(('feature', 'Table Lamp'))
        if "Floor" in s: tags.append(('feature', 'Floor Lamp'))
        if "Desk" in s: tags.append(('feature', 'Desk Lamp'))
        if "Uplight" in s: tags.append(('feature', 'Uplight Lamp'))
        if "Tray" in s: tags.append(('feature', 'Tray Lamp'))
        if "Arc" in s: tags.append(('feature', 'Arc Lamp'))
        # Is this how we want to handle materials?
        if "Acrylic" in s: tags.append(('material', 'Acrylic'))
        if "Ceramic" in s: tags.append(('material', 'Ceramic'))
        if "Crystal" in s: tags.append(('material', 'Crystal'))
        if "Glass" in s: tags.append(('material', 'Glass'))
        if "Metal" in s: tags.append(('material', 'Metal'))
        if "Paper" in s: tags.append(('material', 'Paper'))
        if "Poly" in s: tags.append(('material', 'Poly'))
        if "Rattan" in s: tags.append(('material', 'Rattan'))
        if "Shell" in s: tags.append(('material', 'Shell'))
        if "Terracotta" in s: tags.append(('material', 'Terracotta'))
        if "Wood" in s: tags.append(('material', 'Wood'))
        # Finally, handle counts
        if "(2/CN)" in s: name_suffix = "x2"
        if "(4/CN)" in s: name_suffix = "x4"
        setvals('Accessories', 'Lighting')
    elif "Cocktail T" in s:
        pre, post = breakdown(s, "Cocktail TBL" if "TBL" in s else "Cocktail Table")
        if "with Storage" in post: tags.append(('feature', 'Storage'))
        if pre: tags.append(('feature', pre))
        setvals("Living", "Coffee Table")
    elif "Table" in s:
        # Deal with shapes first
        if 'Rectangular' in s or 'RECT' in s: tags.append(('shape', 'Rectangular'))
        elif 'Round' in s:     tags.append(('shape', 'Round'))
        elif 'Square' in s:    tags.append(('shape', 'Square'))
        elif 'Triangle' in s:  tags.append(('shape', 'Triangle'))
        # Table set we are now dealing with can be gotten with command below: since the "-v" terms will all by caught by above
        # cat types.txt | grep "Table" | grep -v "Home Office" | grep -v "Dining" | grep -v "Lamp" | grep -v "Sofa" | grep -v "Cocktail T"
        if "End Table" in s:
            # handle sets
            if "Nesting" in s:
                name_prefix = "Nesting"
                if "2/CN" in s: name_suffix = "x2"
                elif "3/CN" in s: name_suffix = "x3"
            setvals("Living", "End Table")
        elif "Accent Table" in s:
            if "Set of 2" in s: name_suffix = "x2"
            setvals("Living", "Accent Table")
        elif "Console" in s:
            setvals("Living", "Console Table")
        elif "Bar Table" in s:
            # these are outdoor items
            setvals("Outdoor", "Outdoor Table")
        elif "Counter Table" in s or "Counter T" in s:
            if 'Storage' in s: tags.append(('feature'), 'Storage')
            if '5/CN' in s: name_suffix = "Set of 5"
            setvals("Dining", "Counter Height Table")
        elif "Fire Pit" in s:
            # Outdoor tables again
            setvals("Outdoor", "Fire Pit Table")
        else:
            if "EXT" in s: tags.append(('feature', 'Extendable'))
            # Umbrella is outdoors
            if "UMB" in s: raise SkipExc(s)
            # Night Table == Nightstand, to be safe here
            if "Night" in s: raise SkipExc(s)
            # Random shit
            if "OTTO" in s: raise SkipExc(s)
            setvals("Living", "Table")
    elif "Otto" in s:
        # This is a Love/Chaise/otto set
        if "/Otto" in s: raise SkipExc(s) 
        if "2/CN" in s: name_suffix = "x2"
        if "Accent" in s: tags.append(('feature', 'Accent'))
        if "Storage" in s: tags.append(('feature', 'Storage'))
        if "Oversized" in s: tags.append(('feature', 'Oversized'))
        # We're not selling only the cushion
        if "Seat Cushion" in s: raise SkipExc(s)
        setvals("Living", "Ottoman")
    elif "Chest" in s:
        if "Accent" in s: tags.append(('feature', 'Accent'))
        if "Door" in s: tags.append(('feature', 'Has Door'))
        if "Dressing" in s: tags.append(('feature', 'Dressing'))
        if "Lingerie" in s: tags.append(('feature', 'Lingerie'))
        if "Fireplace Option" in s: feature = "with Fireplace"
        if "Two Drawer" in s: tags.append(('feature', 'Two Drawer'))
        if "Three Drawer" in s: tags.append(('feature', 'Three Drawer'))
        if "Four Drawer" in s: tags.append(('feature', 'Four Drawer'))
        if "Five Drawer" in s: tags.append(('feature', 'Five Drawer'))
        if "Six Drawer" in s: tags.append(('feature', 'Six Drawer'))
        # Media chest is different
        if "Media Chest" in s:
            setvals("Bedroom", "Media Chest")
        else:
            setvals("Bedroom", "Chest")
    elif "Dresser" in s:
        if "Fireplace Option" in s: feature = "with Fireplace"
        if "Youth" in s:
            setvals("Youth", "Dresser")
        else:
            setvals("Bedroom", "Dresser")
    elif "Desk" in s:
        if "Bedroom" in s:
            if "Hutch" in s:
                setvals('Bedroom', 'Hutch')
            else:
                setvals('Bedroom', 'Desk')
        if "Adjustable" in s: tags.append(('feature', 'Adjustable Height'))
        if "Drop Front" in s: tags.append(('feature', 'Drop Front'))
        if "Large" in s: size = 'Large'
        if "Small" in s: size = 'Small'
        if "Drop Front" in s: tags.append(('feature', 'Drop Front'))
        if 'Desk and Hutch' in s:
            setvals("Office", "Desk")
        elif 'Hutch' in s:
            if "Tall" in s: tags.append(('feature', 'Tall'))
            if "Short" in s: tags.append(('feature', 'Short'))
            setvals("Office", "Hutch")
        else:
            setvals("Office", "Desk")


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
        category, product_type = figure_out(pt_str.encode('ascii', 'ignore'), additional_info)
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
    name = " ".join(name_parts).encode('ascii', 'ignore')
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
