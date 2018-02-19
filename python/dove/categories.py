
# BEGIN static data

# static definitions to create our store's collections from
_categories = {
    "Bedroom": {
        "Beds": {
            "types": ["Bed"],
        },
        "Benches": {
            "types": ["Bench"],
        },
        "Chests": {
            "types": ["Chest"],
        },
        "Dressers & Mirrors": {
            "types": ["Dresser", "Mirror"],
        },
        "Headboards": {
            "types": ["Headboard"],
        },
        "Media Chests":{
            "types": ["Media Chest"],
        },
        "Nightstands": {
            "types": ["Nightstand"],
        },
        "Wardrobes": {
            "types": ["Wardrobe"],
        },
    },
    "Dining": {
        "Buffets/Hutches/Curios": {
            "types": ["Buffet", "Hutch", "Curio"],
        },
        "Chairs & Stools": {
            "types": ["Chair", "Stool"],
        },
        "Counter Height Tables": {
            "types": ["Table"],
            "tags": ["Counter Height Table"],
        },
        "Dining Tables": {
            "types": ["Table"],
            "tags": ["Dining Table"],
        },
        "Kitchen Islands": {
            "types": ["Kitchen Island"],
        },
        "Servers": {
            "types": ["Server"],
        },
        "Dining Misc.": {
            "types": ["Display Cabinet", "Mirror", "Lazy Susan", "Mini Server",
                      "Wine Cabinet", "Wine Rack"]
        },
    },
    "Living": {
        "Chairs": {
            "types": ["Chair", "Stool"],
        },
        "Chaises & Benches": {
            "types": ["Chaise", "Bench"],
        },
        "Coffee Tables":{
            "types": ["Table"],
            "tags": ["Coffee Table"],
        },
        "Futons": {
            "types": ["Futon"]
        },
        "Love Seats": {
            "types": ["Love Seat"]
        },
        "Ottomans": {
            "types": ["Ottoman"]
        },
        "Recliners": {
            "types": ["Recliner"]
        },
        "Sectionals": {
            "types": ["Sectional"]
        },
        "Side Tables": {
            "types": ["Side Table"]
        },
        "Sofas": {
            "types": ["Sofa"]
        },
        "Sofa Tables": {
            "types": ["Sofa Table"]
        },
        "TV Consoles": {
            "types": ["TV Console"]
        },
    },
    "Office": {
        "Bookshelves": {
            "types": ["Bookshelf"]
        },
        "Desks": {
            "types": ["Desk"]
        },
        "File Cabinets": {
            "types": ["File Cabinet"]
        },
        "Office Chairs": {
            "types": ["Office Chair"]
        },
    },
    "Youth": {
        "Bean Bags": {
            "types": ["Bean Bag"]
        },
        "Bunk Beds": {
            "types": ["Bunk Bed"]
        },
        "Loft Beds": {
            "types": ["Loft Bed"]
        },
        "Beds": {
            "types": ["Bed"],
            "tags": ["Youth"]
        },
        "Trundle Beds": {
            "types": ["Trundle Bed"]
        },
        "Headboards": {
            "types": ["Headboard"],
            "tags": ["Youth"]
        },
        "Chests": {
            "types": ["Chest"],
            "tags": ["Youth"]
        },
        "Dressers & Mirrors": {
            "types": ["Dresser", "Mirror"],
            "tags": ["Youth"]
        },
        "Nightstands": {
            "types": ["Nighstand"],
            "tags": ["Youth"]
        },
        "Youth Chairs": {
            "types": ["Chair"],
            "tags": ["Youth"]
        },
        "Youth Misc.":{
            "types": [
                "Book Shelf",
                "Canopy",
                "Double Door Closet",
                "Futon",
                "Office Chair",
                "Vanity w/ Stool",
            ],
        }
    },
}
''' TODO
    "Outdoor": {
        "Outdoor Benches",
        "Outdoor Chairs",
        "Outdoor Coffee Sets",
        "Outdoor Daybeds",
        "Outdoor Dining Sets",
        "Outdoor Sectionals",
        "Outdoor Sofas",
        "Outdoor Swings",
        "Outdoor Umbrellas",
    },
    "Mattress": {
        "Box Springs",
        "Bunky Boards",
        "Memory Foam Mattresses",
        "Metal Frames",
        "Spring Coil Mattresses",
    },
    "Accessories": {
        "Clocks",
        "Coat Racks",
        "Display Cabinets",
        "Game Tables",
        "Home Accents",
        "Jewelry Armories",
        "Lighting",
        "Mirrors",
        "Pillows & Throws",
        "Room Dividers",
        "Rugs",
        "Serving Carts",
        "Shoe Racks",
        "Storage Trunks",
        "Tray Tables",
        "Vanities",
        "Wall Decor",
        "Wine Bars & Racks",
    },
}
'''

_valid_types = set()
for _cat, cat_data in _categories.iteritems():
    for _subcat, subcat_data in cat_data.iteritems():
        for t in subcat_data['types']:
            _valid_types.add(t)

aliases = {
    "armoires": "Armoire",
    "beanbags": "Bean Bag",
    "beds": "Bed",
    "bedframes": "Bed",
    "bedrooms": "Bedroom",
    "benches": "Bench",
    "bookshelf": "Book Shelf",
    "bookshelves": "Book Shelf",
    "buffets": "Buffet",
    "chairs": "Chair",
    "chests": "Chest",
    "coffeetable": "Coffee Table",
    "coffeetables": "Coffee Table",
    "consoletable": "Console Table",
    "consoletables": "Console Table",
    "countertable": "Counter Height Table",
    "countertables": "Counter Height Table",
    "counterheighttables": "Counter Height Table",
    "curios": "Curio",
    "desks": "Desk",
    "diningtables": "Dining Table",
    "dressers": "Dresser",
    "endtable": "Sofa Table",
    "entertainmentconsole": "TV Console",
    "filecabinets": "File Cabinet",
    "headboards": "Headboard",
    "hutches": "Hutch",
    "jewelrydrawers": "Jewelry Drawer",
    "mediachests": "Media Chest",
    "mirrors": "Mirror",
    "nightstands": "Nightstand",
    "pier": "TV Console",
    "servers": "Server",
    "sideboard": "Server",
    "stools": "Stool",
    "tables": "Table",
}

# END static data

class InvalidProductTypeError(ValueError):
    pass

def is_valid(subcategory, category):
    """Is the given subcategory a valid value, and is contained in category?"""
    return subcategory in _categories[category]

def subcategories(category):
    return _categories[category]

def resolve(name):
    """Turn some bullshit like "Night stands" --> "Nightstand"
    <string> --> <a product type in our store>
    """
    if name in _valid_types:
        return name

    # create a key that's all lowercase and strips any spaces
    k = name.lower().replace(' ', '')

    try:
        return aliases[k]
    except KeyError:
        raise InvalidProductTypeError(
            "'%s' couldn't be resolved to a valid category string."
            " Update the aliases dict." % (name))

def resolve_to_tag(name):
    return resolve(name)