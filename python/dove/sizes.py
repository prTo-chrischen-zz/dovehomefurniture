
_sizes = {
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

def resolve(name):
    # create a key that's all lowercase and strips any spaces
    k = name.lower().replace(' ', '')

    try:
        return _sizes[k]
    except KeyError:
        raise ValueError("'%s' couldn't be resolved to a valid size string."
                         " Update the sizes dict." % (name))


_ordering = [
    "Twin",
    "Full",
    "Queen",
    "King",
    "C. King",
    "E. King",
]
def size_cmp(a, b):
    if a in _ordering and b in _ordering:
        return cmp(_ordering.index(a), _ordering.index(b))
    else:
        return cmp(a, b)
