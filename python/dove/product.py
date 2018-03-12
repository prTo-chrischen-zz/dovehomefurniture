import base64
import os
from collections import defaultdict

from dove import categories, sizes

from dove import shopify_config
shopify_config.setup()

import shopify



class VariantError(StandardError):
    def __init__(self, sku, duplicate_combo, existing_sku):
        self.sku = sku
        self.duplicate = duplicate_combo
        self.existing = existing_sku

    def __str__(self):
        return ("Combination %s already exists in %s (new sku=%s)"
                % (str(self.duplicate), self.existing, self.sku))

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
        self.product_type = categories.resolve(product_type, category)
        self.category = category
        self.description = description
        self.description_items = []
        self.style = style
        self.vendor = vendor
        self.colors = set()
        self.sizes = {}
        self.images = defaultdict(list)
        self.image_urls = []
        self.variants = []
        self.variant_combos = {}

        # after build_options(), this will be something like
        # {'Color': 'option1', 'Size': 'option2'}
        self.options_map = None

        # store dimensions per size. For the cases where a product has no sizes,
        # use this as an override
        self.dimensions = None

        self.features = set()

        # build the minimum tags first
        self.tags = set([category.lower(),
                         self.product_type,
                         ])
        if style:
            self.add_tag('style', style)

        self.enforce_bed_sizing = (self.product_type == "Bed")

    def __str__(self):
        s = "== %s - %s" % (self.name, self.product_type)
        s +="\n\tsizes=%s" % str(self.sizes.keys())
        s +="\n\tcolors=%s" % str(self.colors)
        s +="\n\tfeatures=%s" % str(self.features)
        return s


    def add_tag(self, tag_type, tag):
        if not tag.strip():
            raise ValueError("Tag was empty!")
        self.tags.add('%s:%s' % (tag_type, tag))

    def add_image_url(self, url):
        self.image_urls.append(url)

    def resolve_size(self, size):
        if self.enforce_bed_sizing:
            return sizes.resolve(size)
        return size

    def add_variant(self, size, sku, price, weight, dimensions,
                    color=None, image=None, feature=None):
        size = self.resolve_size(size) if size else None

        # Shopify doesn't like it when you try to add 2 variants with the same
        # options, so try to figure that out first and return an error
        combo = (color, size, feature)
        if combo in self.variant_combos:
            raise VariantError(sku, combo, self.variant_combos[combo])
        self.variant_combos[combo] = sku

        variant_idx = len(self.variants)
        variant = {
                'sku': sku,
                'price': (price if price else 0),
                'weight': (float(weight) if weight else 0),
                'weight_unit': 'lb',
                'dimensions': dimensions,
                'options': {},  # for use in build_variants()
            }

        if color:
            self.colors.add(color)
            variant['options']['Color'] = color
        else:
            if self.colors:
                # There are already colors for this product, so just use one
                # of them. Otherwise you'll get a Color dropdown in the product
                # page with "Default Title" as the value for this variant.
                variant['options']['Color'] = \
                    self.variants[-1]['options']['Color']

        if size:
            if size not in self.sizes:
                self.sizes[size] = dimensions
            variant['options']['Size'] = size
        elif dimensions:
            # We'll get here if a product has no size. We still want dimensions
            self.dimensions = dimensions

        if feature:
            self.features.add(feature)
            variant['options']['Feature'] = feature

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
            'images': list(self.images.keys()) + self.image_urls,
            'vendor': self.vendor,
            'tags': list(sorted(self.tags)),
            'options': self.build_options(),
            'options_map': self.options_map,
            'variants': self.build_variants(),
            }

    def set_description_items(self, items):
        self.description_items = items

    def build_description(self):
        desc = self.description

        desc = self.description.replace('\n', '<br/>')

        if self.description_items:
            desc += '<br/><br/><ul class="product-desc-list">'
            for i in self.description_items:
                desc += '<li>%s</li>' % (i)
            desc += '</ul>'

        if self.sizes or self.dimensions:
            # build a table for displaying dimensions
            desc += (
                '<br/><br/>'
                '<table class="dimensions-table">'
                '<thead><tr><th>Dimensions</th></tr></thead>'
                '<tbody>'
            )
            if self.dimensions:
                # use the dimensions override first
                desc += "<tr><td>%s</td></tr>" % (self.dimensions)
            else:
                # otherwise build a table from the sizes
                for size in sorted(self.sizes.keys(), cmp=sizes.size_cmp):
                    dims = self.sizes[size]
                    desc += "<tr><td>%s</td><td>%s</td></tr>" % (size, dims)
            desc += "</tbody></table>"

        # because sometimes the descriptions or dimension text in the source
        # data can have bullshit characters, sanitize the bitch
        decoded = desc.decode('utf-8', 'ignore')
        encoded = decoded.encode('utf-8')

        return encoded

    def build_options(self):
        # thing that Shopify API wants
        options = []

        # for use in build_variants()
        self.options_map = {}

        if self.colors:
            options.append({
                'name': 'Color',
                'values': [c for c in sorted(self.colors)]
            })
            self.options_map['Color'] = 'option%d' % (len(options))
        if self.sizes:
            options.append({
                'name': 'Size',
                'values': [s for s in
                           sorted(self.sizes.keys(), cmp=sizes.size_cmp)]
            })
            self.options_map['Size'] = 'option%d' % (len(options))
        if self.features:
            options.append({
                'name': 'Feature',
                'values': [f for f in sorted(self.features)]
            })
            self.options_map['Feature'] = 'option%d' % (len(options))

        return options

    def build_variants(self):
        if self.options_map is None:
            raise RuntimeError("build_options() must be run first!")

        variants = []

        # go through and replace all the 'options' blocks with actual
        # 'option#' keys, corresponding to our options list
        for const_variant in self.variants:
            # keep the original data pristine
            variant = const_variant.copy()

            for opt_name, new_k in self.options_map.iteritems():
                try:
                    value = variant['options'][opt_name]
                except KeyError as e:
                    # if one variant is missing one, use 'Standard'
                    # (otherwise Shopify will use the string "Default Title")
                    value = 'Standard'
                variant[new_k] = value

            del variant['options']
            variants.append(variant)

        return variants

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

        if self.image_urls:
            p.images = [{'src': url} for url in self.image_urls]

        p.save()

        if p.errors:
            print p.errors.full_messages()
            raise RuntimeError("Failed to create product '%s'" % self.name)

        # create images afterwards, so we can associate them with variant IDs
        # (p.id doesn't exist until save())
        self.create_images(p.id, p.variants)

    def find_uploaded(self, fields=['id', 'tags'], **filters):
        """Find the uploaded equivalent of this product, if it exists.

        Returns
            shopify.Product object, or None if no such product exists
        """
        products = shopify.Product.find(limit=2, page=1, fields=fields,
                                        **filters)
        if len(products) > 1:
            raise ValueError("Found more than one product that matches... wtf?")
        elif not products:
            return None
        return products[0]
