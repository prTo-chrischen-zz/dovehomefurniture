from collections import defaultdict


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
        "Desks": {
            "types": ["Desk", "Hutch"],
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
        "Media Chests": {
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
            "types": ["Counter Height Table"],
            "tags": ["Counter Height Table"],
        },
        "Dining Tables": {
            "types": ["Table"],
            "tags": ["Dining Table"],
        },
        "Kitchen Islands": {
            "types": ["Kitchen Island", "Kitchen Cart"],
        },
        "Servers": {
            "types": ["Server"],
        },
        "Dining Misc.": {
            "types": ["Display Cabinet", "Mirror", "Lazy Susan", "Mini Server",
                      "Wine Cabinet", "Wine Rack", "Bench"]
        },
    },
    "Living": {
        "Cabinets": {
            "types": ["Storage Cabinet", "Cabinet"],
        },
        "Chairs": {
            "types": ["Chair"],
        },
        "Chaises & Benches": {
            "types": ["Chaise", "Bench", "Storage Bench"],
        },
        "Coffee Tables":{
            "types": ["Table", "Coffee Table", "Coffee Table Set"],
            "tags": ["Coffee Table"],
        },
        "Futons": {
            "types": ["Futon"]
        },
        "Love Seats": {
            "types": ["Love Seat"]
        },
        "Ottomans": {
            "types": ["Ottoman", "Pouf"]
        },
        "Recliners": {
            "types": ["Recliner"]
        },
        "Sectionals": {
            "types": ["Sectional"]
        },
        "Living Tables": {
            "types": ["Side Table", "Sofa Table", "Console Table", "Accent Table"]
        },
        "Sofas": {
            "types": ["Sofa"]
        },
        "Entertainment Consoles": {
            "types": [
                "Entertainment Console",
                "TV Console",
                "Pier Cabinet",
                "Bridge",
                "Hutch",
                "Media Cabinet",
            ]
        },
        "Shelves": {
            "types": ["Book Shelf", "Shelf"]
        }
    },
    "Office": {
        "Bookshelves": {
            "types": ["Book Shelf"],
        },
        "Desks": {
            "types": ["Desk", "Hutch"]
        },
        "File Cabinets": {
            "types": ["File Cabinet", "Cabinet"]
        },
        "Office Chairs": {
            "types": ["Office Chair"]
        },
        "Office Tables": {
            "types": ["Office Table"]
        },
    },
    "Youth": {
        "Beds": {
            "types": ["Bed"],
            "tags": ["Youth"]
        },
        "Bunk Beds": {
            "types": ["Bunk Bed"]
        },
        "Daybeds": {
            "types": ["Daybed"],
            "tags": ["Youth"]
        },
        "Loft Beds": {
            "types": ["Loft Bed"]
        },
        "Trundle Beds": {
            "types": ["Trundle Bed"]
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
            "types": ["Nightstand"],
            "tags": ["Youth"]
        },
        "Youth Misc.":{
            "types": [
                "Bean Bag",
                "Bench",
                "Book Case",
                "Book Shelf",
                "Coat Rack",
                "Canopy",
                "Chair",
                "Desk",
                "Drawer",
                "Double Door Closet",
                "Futon",
                "Hutch",
                "Media Chest",
                "Office Chair",
                "Ottoman",
                "Shelf",
                "Table",
                "Vanity",
            ],
            "tags": ["Youth"],
        }
    },
    "Outdoor": {
        "Outdoor Benches": { "types": ["Outdoor Bench"] },
        "Outdoor Chairs": {"types": ["Outdoor Chair"]},
        "Outdoor Tables": {
            "types": ["Outdoor Table", "Fire Pit Table"]
        },
    },
    "Accessories": {
        "Lamps": {"types": ["Lamp"]},
        "Mirrors": {"types": ["Mirror"]},
        "Rugs": {"types": ["Rug"]},
        "Under Bed Storage": {"types": ["Under Bed Storage"]},
        "Wall Decor": {"types": ["Wall Decor"]},
    },
}
''' TODO
    "Outdoor": {
        "Outdoor Benches",
        "Outdoor Coffee Sets",
        "Outdoor Daybeds",
        "Outdoor Dining Sets",
        "Outdoor Sectionals",
        "Outdoor Sofas",
        "Outdoor Swings",
        "Outdoor Table",
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
        "Bedding",
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

_valid_types = defaultdict(set)
for cat, cat_data in _categories.iteritems():
    for _subcat, subcat_data in cat_data.iteritems():
        for t in subcat_data['types']:
            _valid_types[cat].add(t)

aliases = {
    "bedframe": "Bed",
    "bookshelf": "Book Shelf",
    "endtable": "Sofa Table",
    "entertainmentconsole": "TV Console",
    "nightstand": "Nightstand",
    "pier": "TV Console",
}

# END static data

class InvalidProductTypeError(ValueError):
    pass

def is_valid(subcategory, category):
    """Is the given subcategory a valid value, and is contained in category?"""
    return subcategory in _categories[category]

def subcategories(category):
    return _categories[category]

def resolve(name, category):
    """Turn some bullshit like "Night stands" --> "Nightstand"
    <string> --> <a product type in our store>

    and also validate that it's a valid type for the category
    """
    # check if we have an alias for it
    # create a key that's all lowercase and strips any spaces
    k = name.lower().replace(' ', '')
    if k in aliases:
        name = aliases[k]

    if name not in _valid_types[category]:
        raise InvalidProductTypeError(
            "'%s' couldn't be resolved to a valid category string."
            " Update the types dict in '%s'" % (name, category))

    return name

