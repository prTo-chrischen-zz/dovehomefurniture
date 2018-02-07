import base64
import os

from dove import categories, sizes

from dove import shopify_config
shopify_config.setup()

import shopify


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
        self.variant_dimensions = {}

        # build the minimum tags first
        self.tags = set([category.lower(),
                         categories.resolve(product_type),
                         ])

    def add_tag(self, tag):
        # TODO process the tag here?
        self.tags.add(tag)

    def add_image(self, image_path):
        if not os.path.exists(image_path):
            raise ValueError("Image path '%s' doesn't exist" % image_path)
        self.images.add(image_path)

    def add_color(self, color):
        self.options.add(color)

    def add_variant(self, sku, size, weight=None, price=None,
                    dimensions=None):

        size = sizes.resolve(size) if size else ''

        weight = float(weight) if weight else 0

        self.variants[size] = {
            'sku': sku,
            'option1': size,
            'price': (price if price else 0),
            'weight': weight,
            'weight_unit': 'lb',
            }

        if dimensions.strip():
            self.variant_dimensions[size] = dimensions

    def data(self):
        """Purely for reference -- what shopify wants to be set when you create
        a new Product record.

        TODO use some setattr magic and use this dict to drive upload()
        """

        return {
            'title': self.name,
            'product_type': self.product_type,
            'body_html': self.build_description(),
            'images': list(self.images),
            'vendor': self.vendor,
            'tags': list(sorted(self.tags)),
            'variants': self.build_variants(),
            }

    def build_description(self):
        desc = self.description

        if self.variant_dimensions:
            # build a table for displaying dimensions
            desc += (
                '<br/><br/>'
                '<table class="dimensions-table">'
                '<thead><tr><th>Dimensions</th></tr></thead>'
                '<tbody>'
            )
            for size in sorted(self.variant_dimensions.keys(), cmp=sizes.size_cmp):
                dims = self.variant_dimensions[size]
                desc += "<tr><td>%s</td><td>%s</td></tr>" % (size, dims)
            desc += "</tbody><table>"

        # because sometimes the descriptions or dimension text in the source
        # data can have bullshit characters, sanitize the bitch
        desc = desc.decode('utf-8', 'ignore').encode('utf-8')

        return desc

    def build_images(self):
        data = []
        for image_path in self.images:
            image = shopify.Image()
            with open(image_path, 'rb') as fp:
                image.attach_image(fp.read())
            data.append(image)
        return data

    def build_variants(self):
        # want to make sure the variants are sorted by sizes
        # ie. Twin, Full, Queen, King
        return [self.variants[i]
                for i in sorted(self.variants.keys(), cmp=sizes.size_cmp)]

    def upload(self):
        """Upload shit to shopify """
        p = shopify.Product()

        p.title = self.name
        p.product_type = self.product_type
        p.body_html = self.build_description()
        p.vendor = self.vendor
        p.tags = list(sorted(self.tags))
        p.variants = self.build_variants()

        if self.images:
            p.images = self.build_images()

        p.save()

        if p.errors:
            print p.errors.full_messages()
            raise RuntimeError("Failed to create product '%s'" % self.name)

