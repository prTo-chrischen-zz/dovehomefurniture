
# BEGIN static data
_categories = {
    "Bedroom": [
        "Beds",
        "Benches",
        "Chests",
        "Dressers & Mirrors",
        "Headboards",
        "Media Chests",
        "Nightstands",
        "Wardrobes",
    ],
    "Dining": [
        "Buffets/Hutches/Curios",
        "Chairs & Stools",
        "Counter Height Tables",
        "Dining Tables",
        "Kitchen Islands",
        "Servers",
    ],
    "Living": [
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
    ],
    "Youth": [
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
    ],
    "Office": [
        "Bookshelves",
        "Desks",
        "File Cabinets",
        "Office Chairs",
    ],
    "Outdoor": [
        "Outdoor Benches",
        "Outdoor Chairs",
        "Outdoor Coffee Sets",
        "Outdoor Daybeds",
        "Outdoor Dining Sets",
        "Outdoor Sectionals",
        "Outdoor Sofas",
        "Outdoor Swings",
        "Outdoor Umbrellas",
    ],
    "Mattress": [
        "Box Springs",
        "Bunky Boards",
        "Memory Foam Mattresses",
        "Metal Frames",
        "Spring Coil Mattresses",
    ],
    "Accessories": [
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
    ],
}

aliases = {
    "armoires": "Armoire",
    "beds": "Bed",
    "bedrooms": "Bedroom",
    "benches": "Bench",
    "bookshelves": "Book Shelf",
    "chairs": "Chair",
    "chests": "Chest",
    "coffeetables": "Coffee Table",
    "consoletables": "Console Table",
    "countertables": "Counter Table",
    "desks": "Desk",
    "dressers": "Dresser",
    "endtables": "End Table",
    "entertainmentconsoles": "Entertainment Console",
    "filecabinets": "File Cabinet",
    "headboards": "Headboard",
    "jewelrydrawers": "Jewelry Drawer",
    "mediachests": "Media Chest",
    "mirrors": "Mirror",
    "nightstands": "Nightstand",
    "piers": "Pier",
    "sideboards": "Sideboard",
    "stools": "Stool",
    "tables": "Table",
}

sizes = {
    "cal.king": "C. King",
    "e.king": "E. King",
    "full": "Full",
    "king": "King",
    "queen": "Queen",
    "queen/full": "Queen/Full",
    "twin": "Twin",
    "large": "Large",
    "small": "Small",
}
# END static data


def subcategories(category):
    return _categories[category]

def resolve_size(name):
    # create a key that's all lowercase and strips any spaces
    k = name.lower().replace(' ', '')

    try:
        return sizes[k]
    except KeyError:
        raise ValueError("'%s' couldn't be resolved to a valid size string."
                         " Update the sizes dict." % (name))

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
    return resolve(name).lower().replace(' ', '-')