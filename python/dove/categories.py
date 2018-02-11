
# BEGIN static data

# static definitions to create our store's collections from
_categories = {
    "Bedroom": {
        "Beds": {
            "types": ["Bed"],
            "tags": [],
        },
        "Benches": {
            "types": ["Bench"],
            "tags": [],
        },
        "Chests": {
            "types": ["Chest"],
            "tags": [],
        },
        "Dressers & Mirrors": {
            "types": ["Dresser", "Mirror"],
            "tags": [],
        },
        "Headboards": {
            "types": ["Headboard"],
            "tags": [],
        },
        "Media Chests":{
            "types": ["Media Chest"],
            "tags": [],
        },
        "Nightstands": {
            "types": ["Nightstand"],
            "tags": [],
        },
        "Wardrobes": {
            "types": ["Wardrobe"],
            "tags": [],
        },
    },
    "Dining": {
        "Buffets/Hutches/Curios": {
            "types": ["Buffet", "Hutch", "Curio"],
            "tags": [],
        },
        "Chairs & Stools": {
            "types": ["Chair", "Stool"],
            "tags": [],
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
            "tags": [],
        },
        "Servers": {
            "types": ["Server"],
            "tags": [],
        },
    },
    "Living": {
        "Chairs",
        "Chaises & Benches",
        "Coffee Tables",
        "Futons",
        "Love Seats",
        "Ottomans",
        "Recliners",
        "Sectionals",
        "Side Tables",
        "Sofas",
        "Sofa Tables",
        "TV Consoles",
    },
    "Youth": {
        "Bean Bags",
        "Bunk Beds",
        "Loft Beds",
        "Beds",
        "Trundle Beds",
        "Headboards",
        "Chests",
        "Dressers & Mirrors",
        "Nightstands ",
        "Youth Chairs",
    },
    "Office": {
        "Bookshelves",
        "Desks",
        "File Cabinets",
        "Office Chairs",
    },
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

aliases = {
    "armoires": "Armoire",
    "beds": "Bed",
    "bedrooms": "Bedroom",
    "benches": "Bench",
    "bookshelves": "Book Shelf",
    "buffets": "Buffet",
    "chairs": "Chair",
    "chests": "Chest",
    "coffeetables": "Coffee Table",
    "consoletables": "Console Table",
    "countertables": "Counter Height Table",
    "counterheighttables": "Counter Height Table",
    "desks": "Desk",
    "diningtables": "Dining Table",
    "dressers": "Dresser",
    "endtables": "End Table",
    "entertainmentconsoles": "Entertainment Console",
    "filecabinets": "File Cabinet",
    "headboards": "Headboard",
    "hutches": "Hutch",
    "jewelrydrawers": "Jewelry Drawer",
    "mediachests": "Media Chest",
    "mirrors": "Mirror",
    "nightstands": "Nightstand",
    "piers": "Pier",
    "servers": "Server",
    "sideboards": "Sideboard",
    "stools": "Stool",
    "tables": "Table",
}

# END static data


def is_valid(subcategory, category):
    """Is the given subcategory a valid value, and is contained in category?"""
    return subcategory in _categories[category]

def subcategories(category):
    return _categories[category]

def resolve(name):
    """Turn some bullshit like "Night stands" --> "Nightstand"
    <string> --> <our store's category displayname>
    """
    # create a key that's all lowercase and strips any spaces
    k = name.lower().replace(' ', '')

    try:
        return aliases[k]
    except KeyError:
        raise ValueError("'%s' couldn't be resolved to a valid category string."
                         " Update the aliases dict." % (name))

def resolve_to_tag(name):
    return resolve(name)