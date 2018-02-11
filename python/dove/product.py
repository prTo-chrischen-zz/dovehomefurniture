import base64
import os
from collections import defaultdict

from dove import categories, sizes

from dove import shopify_config
shopify_config.setup()

import shopify



class VariantError(StandardError):
    pass

_products = {}
def get_or_make_product(product_key, name, category, product_type, description,
                        vendor, style):
    global _products
    if product_key in _products:
        product = _products[product_key]
    else:
        product = Product(name, category, product_type, description, vendor,
                          style)
        _products[product_key] = product
    return product

def get_products():
    for pkey in sorted(_products.keys()):
        yield pkey, _products[pkey]

class Product(object):
    def __init__(self,
                 name,
                 category,
                 product_type,
                 description,
                 vendor,
                 style
                 ):

        self.name = name
        self.product_type = categories.resolve(product_type)
        self.category = category
        self.description = description
        self.style = style
        self.vendor = vendor
        self.colors = set()
        self.sizes = {}
        self.images = defaultdict(list)
        self.variants = []
        self.variant_combos = set()

        # specific to beds
        self.features = set()

        # build the minimum tags first
        self.tags = set([category.lower(),
                         categories.resolve(product_type),
                         ])
        if style:
            self.add_tag('style', style)

    def add_tag(self, tag_type, tag):
        if not tag.strip():
            raise ValueError("Tag was empty!")
        self.tags.add('%s:%s' % (tag_type, tag))

    def add_variant(self, size, sku, price, weight, dimensions, color, image,
                    feature=None):
        size = sizes.resolve(size) if size else None

        # Shopify doesn't like it when you try to add 2 variants with the same
        # options, so try to figure that out first and return an error
        combo = (color, size, feature)
        if combo in self.variant_combos:
            raise VariantError("Already have a variant for combination %s (sku=%s)"
                               % (str(combo), sku))
        self.variant_combos.add(combo)

        variant_idx = len(self.variants)
        variant = {
                'sku': sku,
                'price': (price if price else 0),
                'weight': (float(weight) if weight else 0),
                'weight_unit': 'lb',
                'dimensions': dimensions,
            }

        if color:
            self.colors.add(color)
            variant['option1'] = color
        else:
            if self.colors:
                # There are already colors for this product, so just use one
                # of them. Otherwise you'll get a Color dropdown in the product
                # page with "Default Title" as the value for this variant.
                variant['option1'] = self.variants[len(self.variants)-1]['option1']

        if size:
            if size not in self.sizes:
                self.sizes[size] = dimensions
            variant['option2'] = size

        if feature:
            self.features.add(feature)
            variant['option3'] = feature

        self.variants.append(variant)

        # store a map of images -> variant indices, so that we can associate
        # them back afterwards
        if image:
            self.images[image].append(variant_idx)

    def data(self):
        """Purely for reference -- what shopify wants to be set when you create
        a new Product record.

        TODO use some setattr magic and use this dict to drive upload()
        """

        return {
            'title': self.name,
            'product_type': self.product_type,
            'body_html': self.build_description(),
            'images': self.images,
            'vendor': self.vendor,
            'tags': list(sorted(self.tags)),
            'options': self.build_options(),
            'variants': self.build_variants(),
            }

    def build_description(self):
        desc = self.description

        if self.sizes:
            # build a table for displaying dimensions
            desc += (
                '<br/><br/>'
                '<table class="dimensions-table">'
                '<thead><tr><th>Dimensions</th></tr></thead>'
                '<tbody>'
            )
            for size in sorted(self.sizes.keys(), cmp=sizes.size_cmp):
                dims = self.sizes[size]
                desc += "<tr><td>%s</td><td>%s</td></tr>" % (size, dims)
            desc += "</tbody><table>"

        # because sometimes the descriptions or dimension text in the source
        # data can have bullshit characters, sanitize the bitch
        desc = desc.decode('utf-8', 'ignore').encode('utf-8')

        return desc

    def build_options(self):
        options = [
            # assume we always have colors
            {
                # option1
                'name': 'Color',
                'values': [c for c in sorted(self.colors)]
            },
        ]
        if self.sizes:
            options.append({
                # option2
                'name': 'Size',
                'values': [s for s in
                           sorted(self.sizes.keys(), cmp=sizes.size_cmp)]
                # TODO might need to differentiate sort by product_type
            })
        if self.features:
            options.append({
                'name': 'Feature',
                'values': [f for f in sorted(self.features)]
            })
        return options

    def build_variants(self):
        # clean up all our variants so that if any of them have missing options,
        # we put a value of "Standard" (otherwise we get "Default Title")
        if self.features:

            swap_key = None
            if not self.sizes:
                # HACK: since features are stored in the variant data as
                # option3, we need to bump it up to option2
                swap_key = 'option2'

            for variant in self.variants:
                if 'option3' not in variant:
                    variant['option3'] = "Standard"

                if swap_key:
                    variant['option2'] = variant['option3']
                    del variant['option3']

        return self.variants

    def create_images(self, product_id, variants):
        """variants: shopify Product Variant object
        product_id: shopify Product ID
        """
        for image_path, variant_indices in self.images.iteritems():

            # create the image
            image = shopify.Image()
            with open(image_path, 'rb') as fp:
                image.attach_image(fp.read())

            # associate it with the right variants
            image.product_id = product_id
            image.variant_ids = [variants[i].id for i in variant_indices]
            image.save()

    def upload(self):
        """Upload shit to shopify """
        p = shopify.Product()

        p.title = self.name
        p.product_type = self.product_type
        p.body_html = self.build_description()
        p.vendor = self.vendor
        p.tags = list(sorted(self.tags))
        p.options = self.build_options()
        p.variants = self.build_variants()

        p.save()

        if p.errors:
            print p.errors.full_messages()
            raise RuntimeError("Failed to create product '%s'" % self.name)

        # create images afterwards, so we can associate them with variant IDs
        # (p.id doesn't exist until save())
        self.create_images(p.id, p.variants)
