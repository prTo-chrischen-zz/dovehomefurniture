
from dove import categories

class Product(object):
    def __init__(self,
                 name,
                 category,
                 product_type,
                 description,
                 vendor
                 ):

        self.name = name
        self.product_type = categories.resolve(product_type)
        self.category = category
        self.description = description
        self.options = set()
        self.variants = {}
        self.images = set()
        self.vendor = vendor

        # build the minimum tags first
        self.tags = set([category.lower(),
                         categories.resolve_to_tag(product_type),
                         ])

    def add_tag(self, tag):
        # TODO process the tag here?
        self.tags.add(tag)

    def add_image(self, image_path):
        self.images.add(image_path)

    def add_color(self, color):
        self.options.add(color)

    def add_variant(self, sku, size, weight=None, price=None, image=None,
                    dimensions=None):

        size = categories.resolve_size(size) if size else ''

        weight = float(weight) if weight else 0

        self.variants[size] = {
            'sku': sku,
            'option1': size,
            'price': (price if price else 0),
            'weight': weight,
            'weight_unit': 'lb',
            'image': image,
            'dimensions': dimensions,
            }

    def data(self):
        return {
            'title': self.name,
            'body_html': self.description,
            'product_type': self.product_type,
            'images': list(self.images),
            'vendor': self.vendor,
            'tags': list(self.tags),
            'variants': self.variants,
            }

    def json(self):
        return json.dumps(self.data())