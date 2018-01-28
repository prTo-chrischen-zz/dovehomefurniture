
# BEGIN static data
_categories = {
    "Bedroom": [
        "Bed",
        "Bench",
        "Chest",
        "Dresser",
        "Headboard",
        "Media Chest",
        "Mirror",
        "Nightstand"
    ],
}

aliases = {
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
    "mediachests": "Media Chest",
    "mirrors": "Mirror",
    "nightstands": "Nightstand",
    "piers": "Pier",
    "sideboards": "Sideboard",
    "stools": "Stool",
    "tables": "table",
}
# END static data


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
