import cPickle as pickle
import math
import os
import sys
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
    'accessory set',
    'adjustable base',
    'adjustable foot base',
    'adjustable head base',
    'back cushion',
    'bar with marble top',
    'basket',
    'bench seat cushion',
    'better than down',
    'beverage tub',
    'bolt on bed frame',
    'bowl',
    'Box (Set of 2)',
    'bracket',
    'candle holder',
    'console with drink holders',
    'console with storage',
    'corner wedge',
    'corner with cushion',
    'comforter',
    'coverlet set',
    'credenza',
    ' drawer box',
    'duvet cover set',
    'EVC Case Secure Kit',
    'finial',
    'fireplace insert',
    'fire column',
    ' footboard',
    ' foundation',
    ' ftbd',
    'integrated audio',
    'jar',
    'lantern set',
    'loft bin storage',
    'loft drawer storage',
    'lounge w/cushion', # outdoor
    ' mattress',
    'metal frame',
    'milk can set',
    'panel rails',
    ' panels',
    'patio heater',
    'pendant light',
    'photo holder',
    'platform pedestal',
    'podium',
    'poster rails',
    ' posts',
    'photo frame',
    'pop stand',
    'poster canopy',
    'P.O.S. Station', # wtf is this?
    'quilt set',
    'rails', # We only want Headboards to identify beds
    ' riser',
    'roll slat',
    'sculpture',
    'seat cushion',
    ' slats',
    'sofa/love sec/end tbls', # bullshit outdoor crap
    'storage box',
    'storage drawers',
    'storage shelf',
    'storage step',
    'swing',
    'tob set', # beddings
    'tray',
    'throw',
    ' trundle frame',
    ' trundle panel',
    'umbrella',
    'urn',
    'vase',
    'vanity',
    'w/UPH Stools (3/CN)',
    'w/UMB OPT',
    'wall clock',
    'wall shelf',
    'wall sconce',
    'Replaced by W635-134 Pier', # Old category they're too lazy to remove
    "HYBRID UNIT", # Store display units for mattress cross sections
)

# trivial mappings that don't require code
cat_map = {
    'Console': ('Living', 'Cabinet'),
    'Curio': ('Dining', 'Curio'),
    'Medium Rug': ('Accessories', 'Rug'),
    'Kitchen Cart': ('Dining', 'Kitchen Cart'),
    'Kitchen Island': ('Dining', 'Kitchen Island'),
    'Pouf': ('Living', 'Pouf'),
    'Serving Cart': ('Dining', 'Server'),
    'Shelf': ('Living', 'Shelf'),
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

    if "loveseat" in low_s:
        # only care about individual loveseats, other things are
        # components of sectionals
        if s in ['Loveseat', 'Reclining Loveseat', 'Reclining Power Loveseat']:
            if "Reclining" in s or "REC" in s:
                tags.append(('feature', 'Reclining'))
            if "Power" in s:
                tags.append(('feature', "Power"))
                feature = "Power"
            setvals("Living", "Love Seat")
        else:
            raise SkipExc(s)
    elif "Home Office" in s :
        if 'Desk Chair' in s:
            if '(2/CN)' in s: name_suffix = "x2"
            setvals("Office", "Office Chair")
        elif "Desk" in s:
            if 'Small' in s: size = "Small"
            elif 'Large' in s: size = "Large"
            elif 'Short' in s: size = "Short"
            elif 'Tall' in s: size = "Tall"
            if "Drop Front" in s: tags.append(('feature', 'Drop Down Front'))
            if 'Desk Hutch' in s: feature = "w/ Hutch"
            setvals("Office", "Desk")
        elif 'Cabinet' in s:
            setvals("Office", "Cabinet")
        elif 'Table' in s:
            setvals("Office", "Office Table")

    elif "Dining" in s or 'DRM' in s:
        if "Chair" in s:
            if "UPH" in s: tags.append(('feature', 'Upholstered'))
            if 'Arm' in s: feature = 'Arm'
            if 'Side' in s: feature = 'Side'
            if '(2/CN)' in s: name_suffix = "x2"
            setvals("Dining", "Chair")
        elif "Table" in s or 'TBL' in s:
            if "UMB" in s:
                # this has an umbrella option, and is an outdoor table
                tags.append(('feature', "Umbrella"))
                setvals("Outdoor", "Outdoor Table")
            else:
                if "Dining Table" in s:
                    if "Rectangular" in s: tags.append(('feature', 'Rectangular'))
                    setvals("Dining", "Table")
                elif "Dining Room" in s or 'DRM' in s:
                    if "Top" in s: raise SkipExc(s)
                    if "5/CN" in s: name_suffix = "(5pc Set)"
                    if "6/CN" in s: name_suffix = "(6pc Set)"
                    if "7/CN" in s: name_suffix = "(7pc Set)"
                    if "EXT" in s: tags.append(('feature', 'Extendable'))
                    if "RECT" in s: tags.append(('feature', 'Rectangular'))
                    if "Rectangular" in s: tags.append(('feature', 'Rectangular'))
                    if "Round" in s: tags.append(('feature', 'Round'))
                    if "Counter" in s:
                        setvals("Dining", "Counter Height Table")
                    else:
                        setvals("Dining", "Table")
        elif 'Bench' in s:
            if 'UPH' in s: tags.append(('feature', 'Upholstered'))
            setvals("Dining", "Bench")
        elif "Server" in s:
            setvals("Dining", "Server")
        elif "Buffet" in s:
            setvals("Dining", "Buffet")
        elif "China" in s:
            setvals("Dining", "Display Cabinet")
        elif "Hutch" in s:
            setvals("Dining", "Hutch")
    elif "Recliner" in s or 'RECLINER' in s or "Rocker REC" in s:
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
        if 'Wide' in s:
            name_prefix = "Wide"
            tags.append(('feature', 'Wide'))
        if 'Zero Wall' in s: tags.append(('feature', 'Zero Wall'))
        setvals("Living", "Recliner")
    elif "Headboard" in s or "HDBD" in s:
        if 'Queen/Full' in s:  size = ['Queen', 'Full']
        elif 'Queen/King' in s: size = ['Queen', 'King']
        elif 'Twin/Full' in s: size = ['Twin', 'Full']
        elif 'KG/CK' in s or 'K/CK' in s or 'King/C. King' in s:
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
    elif s.endswith("Upholstered Bed"):
        if "Queen" in s:  size = "Queen"
        elif "King" in s: size = "King"
        tags.append(('feature', 'Upholstered'))
        setvals("Bedroom", "Bed")
    elif "Under Bed Storage" in s:
        # these are optional storage units for beds, add them as options
        if 'Queen/King' in s: size = ['Queen', 'King']
        elif 'Twin/Full' in s: size = ['Twin', 'Full']
        elif 'Full' in s: size = 'Full'
        feature = "w/ Storage"
        setvals("Bedroom", "Bed")
    elif "Media Chest" in s:
        pre, post = breakdown(s, "Media Chest")
        if 'w/' in post:
            tags.append(('feature', post.replace('w/', '')))
        setvals("Bedroom", "Media Chest")
    elif "Night Stand" in s or "Night Table" in s:
        if "Night Stand" in s: pre, post = breakdown(s, "Night Stand")
        elif "Night Table" in s: pre, post = breakdown(s, "Night Table")
        if pre:
            tags.append(('feature', pre))
        if post:
            raise TypeError(s)
        setvals("Bedroom", "Nightstand")
    elif "Chair" in s:
        if "Swivel" in s: tags.append(('feature', "Swivel"))
        if '2/CN' in s: name_suffix = 'x2'
        elif '4/CN' in s: name_suffix = 'x4'
        if 'UPH' in s or 'Upholstered' in s: tags.append(('feature', 'Upholstered'))
        if 'Accent' in s or s=='Chair':
            setvals("Living", "Chair")
        elif 'Lounge' in s or 'Sling' in s:
            setvals("Outdoor", "Outdoor Chair")
        else:
            raise SkipExc(s)
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
    elif "Barstool" in s:
        if 'UPH' or 'Upholstered' in s: tags.append(('feature', 'Upholstered'))
        if 'Double' in s:
            tags.append(('feature', 'Double'))
            name_prefix = "Double"
        if 'Swivel' in s: tags.append(('feature', 'Swivel'))
        if   '2/CN' in s: name_suffix = "x2"
        elif '4/CN' in s: name_suffix = "x4"
        setvals("Dining", "Stool")
    elif "Wall Art" in s or "Wall Decor" in s:
        if   '2/CN' in s: name_suffix = "x2"
        elif '3/CN' in s: name_suffix = "x3"
        elif '4/CN' in s: name_suffix = "x4"
        elif '5/CN' in s: name_suffix = "x5"
        setvals("Accessories", "Wall Decor")
    elif "sofa" in low_s:
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
            if "Sofa Chaise" in s:
                name_suffix = "Chaise"
                tags.append(('feature', "Chaise"))
            if "Sleeper" in s:
                tags.append(('feature', "Sleeper"))
                if "Twin" in s: size = "Twin"
                elif "Full" in s: size = "Full"
                elif "Queen" in s: size = "Queen"
            setvals("Living", "Sofa")
    elif 'cuddler' in low_s:
        # this is a feature of a sectional
        if   'LAF' in s: feature = 'LAF Cuddler'
        elif 'RAF' in s: feature = 'RAF Cuddler'
        setvals("Living", "Sectional")
    elif "chaise" in low_s:
        if "RAF" in s or "LAF" in s:
            # skip these since they're part of sectionals
            raise SkipExc(s)
        setvals("Living", "Chaise")
    elif "Mirror" in s:
        if '2/CN' in s: name_suffix = 'x2'
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
        if "Oversized" in s: size = "Oversized"
        setvals('Living', 'Sectional')
    # Not a Sofa Sleeper otherwise would have been caught above
    # Sectional Sleeper
    elif "Sleeper" in s and "Armless" in s:
        if "Full" in s: size = "Full"
        setvals('Living', 'Sectional')
    # A pier is a tower of a home entertainment center; TV goes in middle of two Piers
    elif "Pier" in s:
        if "Right" in s: feature = 'Right Side'
        elif "Left" in s:  feature = 'Left side'
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
        for lamp_type in ('Table', 'Floor', 'Desk', 'Uplight', 'Tray', 'Arc'):
            if lamp_type in s:
                name_prefix = lamp_type
                tags.append(('feature', '%s Lamp' % (lamp_type)))
                break
        # handle materials
        if "Acrylic" in s: tags.append(('material', 'Acrylic'))
        elif "Ceramic" in s: tags.append(('material', 'Ceramic'))
        elif "Crystal" in s: tags.append(('material', 'Crystal'))
        elif "Glass" in s: tags.append(('material', 'Glass'))
        elif "Metal" in s: tags.append(('material', 'Metal'))
        elif "Paper" in s: tags.append(('material', 'Paper'))
        elif "Poly" in s: tags.append(('material', 'Poly'))
        elif "Rattan" in s: tags.append(('material', 'Rattan'))
        elif "Shell" in s: tags.append(('material', 'Shell'))
        elif "Terracotta" in s: tags.append(('material', 'Terracotta'))
        elif "Wood" in s: tags.append(('material', 'Wood'))
        # Finally, handle counts
        if "(2/CN)" in s:   name_suffix = "x2"
        elif "(4/CN)" in s: name_suffix = "x4"
        setvals('Accessories', 'Lamp')
    elif "Cocktail T" in s:
        pre, post = breakdown(s, "Cocktail TBL" if "TBL" in s else "Cocktail Table")
        if "with Storage" in post: tags.append(('feature', 'Storage'))
        if pre: tags.append(('feature', pre))
        if "Stools" in s: name_suffix = "Set"
        setvals("Living", "Coffee Table")
    elif "Table" in s or "TBL" in s:
        # Deal with shapes first
        if 'Rectangular' in s or 'RECT' in s: tags.append(('shape', 'Rectangular'))
        elif 'Round' in s:     tags.append(('shape', 'Round'))
        elif 'Square' in s:    tags.append(('shape', 'Square'))
        elif 'Triangle' in s:  tags.append(('shape', 'Triangle'))
        if "EXT" in s: tags.append(('feature', 'Extendable'))
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
            if 'Storage' in s: tags.append(('feature', 'Storage'))
            if '5/CN' in s: name_suffix = "(5pc Set)"
            setvals("Dining", "Counter Height Table")
        elif "Fire Pit" in s:
            # Outdoor tables again
            setvals("Outdoor", "Fire Pit Table")
        elif "UMB" in s:
            setvals("Outdoor", "Outdoor Table")
        else:
            setvals("Living", "Table")
    elif "Otto" in s:
        # We're not selling only the cushion
        if "Seat Cushion" in s: raise SkipExc(s)
        # This is a Love/Chaise/otto set
        if "/Otto" in s: raise SkipExc(s)
        if "2/CN" in s: name_suffix = "x2"
        if "Storage" in s:
            tags.append(('feature', 'Storage'))
            feature = "w/ Storage"
        setvals("Living", "Ottoman")
    elif "Chest" in s:
        if "Lingerie" in s: name_prefix = "Lingerie"
        if "Door" in s:
            feature = "w/ Door"
            tags.append(('feature', 'Has Door'))
        if "Two Drawer" in s:     tags.append(('feature', '2 Drawer'))
        elif "Three Drawer" in s: tags.append(('feature', '3 Drawer'))
        elif "Four Drawer" in s:  tags.append(('feature', '4 Drawer'))
        elif "Five Drawer" in s:  tags.append(('feature', '5 Drawer'))
        elif "Six Drawer" in s:   tags.append(('feature', '6 Drawer'))
        setvals("Bedroom", "Chest")
    elif "Dresser" in s:
        if "Fireplace Option" in s: feature = "w/ Fireplace"
        if "Youth" in s:
            setvals("Youth", "Dresser")
        else:
            setvals("Bedroom", "Dresser")
    elif "Desk" in s:
        if "Bedroom" in s:
            if "Desk Hutch" in s: feature = "w/ Hutch"
            setvals('Bedroom', 'Desk')
        else:
            if "Adjustable" in s: tags.append(('feature', 'Adjustable Height'))
            if "Drop Front" in s: tags.append(('feature', 'Drop Down Front'))
            if "Bookcase" in s: tags.append(('feature', 'Bookcase'))
            if "Large" in s: size = 'Large'
            elif "Small" in s: size = 'Small'
            if 'Desk and Hutch' in s:
                setvals("Office", "Desk")
            elif 'Hutch' in s:
                if "Tall" in s: tags.append(('feature', 'Tall'))
                if "Short" in s: tags.append(('feature', 'Short'))
                setvals("Office", "Hutch")
            else:
                setvals("Office", "Desk")
    elif "TV Stand" in s:
        if 'w/' in s:
            stuff = s.split('/w')[-1]
            stuff.replace(' OPT', '')
            stuff.replace(' Option', '')
            stuff.replace("FRPL", "Fireplace")
            feature = "w/ %s" % (stuff)
        if '60' in s:   size = '60"'
        elif '72' in s: size = '72"'
        elif 'Extra Large' in s: size = "Extra Large"
        elif 'Large' in s:       size = "Large"
        setvals("Living", "TV Console")
    elif "Bench" in s:
        if "Upholstered" in s: tags.append(('feature', 'Upholstered'))
        if "Storage Bench" in s:
            setvals("Living", "Storage Bench")
        elif "Park Bench" in s:
            setvals("Outdoor", "Outdoor Bench")
        else:
            setvals("Living", "Bench")
    elif "Pillow" in s:
        raise SkipExc(s)
    elif "Bridge" in s:
        if "Sliding Doors" in s: tags.append(('feature', 'Sliding Doors'))
        setvals("Living", "Bridge")
    elif "Loft Bed" in s:
        if "Twin" in s: size = "Twin"
        setvals("Youth", "Loft Bed")
    elif "Caster Bed" in s or s in ("Daybed", "Day Bed", "Metal Day Bed with Deck"):
        if "Twin" in s: size = "Twin"
        setvals("Youth", "Daybed")
    elif s == "Daybed Trundle Storage":
        feature = "w/ Storage"
        setvals("Youth", "Daybed")
    elif "Bookcase" in s:
        if "Loft" in s:
            # this is actually a bed
            tags.append(('feature', 'Bookcase'))
            setvals("Youth", "Loft Bed")
        else:
            if 'Small' in s: size = "Small"
            elif 'Medium' in s: size = "Medium"
            elif 'Large' in s: size = "Large"
            setvals("Youth", "Book Case")
    elif "Bunk Bed" in s:
        # only want it if it ends with "Bunk Bed", otherwise throw it out
        # because it's something like "Bunk Bed Slats"
        if s.endswith("Bunk Bed") or s.endswith('w/Ladder'):
            if 'Twin/Full' in s: size = 'Twin/Full'
            elif 'Twin/Twin' in s: size = 'Twin/Twin'
            setvals("Youth", "Bunk Bed")
        else:
            raise SkipExc(s)

    if not ret[0] or not ret[1]:
        raise TypeError(s)

    if tags: out_data['tags'] = tags
    if size: out_data['size'] = size
    if feature: out_data['feature'] = feature
    if name_suffix: out_data['name_suffix'] = name_suffix
    if name_prefix: out_data['name_prefix'] = name_prefix

    return ret

def calculate_price(price_str):
    d = int(float(price_str) * 2)
    # round to nearest 10
    return int(math.ceil(d / 10.0)) * 10

uid = 1

ignore_skus = set([
    'W697-34', # duplicate of W697-23
])

for sku, item in items.iteritems():

    if sku in ignore_skus:
        continue

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
        #print "Skip:", str(e)
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

    color = item.get('itemColor')

    pricing = item.find('itemPricing')
    price = None
    if pricing is not None:
        price = calculate_price(pricing.find('unitPrice').text)

    # figure out the image
    img_dir = '/Users/dcheng/desktop/ashley'
    image_node = item.find('image')
    image = None
    if image_node is not None:
        path = os.path.join(img_dir, image_node.get('url'))
        if os.path.exists(path):
            image = path
        else:
            print "[WARNING] no image %s" % path

    # build up the description
    description = None
    fluff = item.find('itemFluff')
    if fluff:
        description = fluff.text
    description_items = [f.text for f in item.findall('itemFeatures/itemFeature')]

    weight = None
    weight_node = item_ident.find("packageCharacteristics/packageDimensions/weight[@unitOfMeasure='Pounds']")
    if weight_node is not None:
        weight = weight_node.get('value')

    dims = None
    item_dims = item_ident.find("itemCharacteristics/itemDimensions/length[@unitOfMeasure='Inches']")
    if item_dims is not None:
        dims = '%s"W x %s"D x %s"H' % (
                item_ident.find("itemCharacteristics/itemDimensions/length[@unitOfMeasure='Inches']").get("value"),
                item_ident.find("itemCharacteristics/itemDimensions/depth[@unitOfMeasure='Inches']").get("value"),
                item_ident.find("itemCharacteristics/itemDimensions/height[@unitOfMeasure='Inches']").get("value"),
            )

    additional_info['color'] = color
    #print "%-46s%-40s%-10s %s" % (name, pt_str, sku, additional_info)

    pkey = name
    if (category=='Dining' and product_type=='Chair') \
       or (category=='Living' and product_type=='Bench') \
       or (category=='Living' and product_type=='Chair') \
       or (category=='Living' and product_type=='Cabinet'):
        # for certain product types, the source data doesn't give us a way
        # to differentiate two products with the same name
        pkey = name + " " + str(uid)
        uid += 1
    p = doveprod.get_or_make_product(
            product_key=pkey,
            name=name,
            category=category,
            product_type=product_type,
            description=description,
            vendor="Ashley",
            style=style)

    sizes = additional_info.get('size', None)
    if not isinstance(sizes, list):
        sizes = [sizes]
    for size in sizes:
        # handle multiple sizes coming out of the product_type parsing
        try:
            p.add_variant(
                size=size,
                sku=sku,
                price=price,
                weight=weight,
                dimensions=dims,
                color=additional_info.get('color', None),
                image=image,
                feature=additional_info.get('feature', None))
        except doveprod.VariantError as e:
            print "[ERROR]", str(e)
            continue

    for tag_type, value in additional_info.get('tags', []):
        p.add_tag(tag_type, value)

    p.set_description_items(description_items)
