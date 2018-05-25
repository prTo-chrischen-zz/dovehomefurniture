import csv
import shopify
import math
import sys
from collections import defaultdict


from dove import categories, shopify_config
shopify_config.setup()

filter_args = {'vendor': 'Ashley'}
query_limit = 250

num_products = shopify.Product.count(**filter_args)
# max 250 items per query, so need to do it by pages
for page in xrange(1, ((num_products-1)/query_limit)+2):
    products = shopify.Product.find(limit=query_limit, page=page,
                                    fields=['id', 'handle', 'vendor', 'title', 'tags'],
                                    **filter_args)
    for product in products:
        print product.title
        possible_style_tags = [i.strip() for i in product.tags.split(',') if 'style-' in i]
        if len(possible_style_tags) > 1:
            raise Exception("why does this product have 2 style tags?")
        if not possible_style_tags:
            print "[WARNING] no style tag for:", product.title
            continue

        num_style_words = len(possible_style_tags[0].split('-')[1:])

        # all-caps this number of words in the title, first-letter cap the rest
        parts = product.title.split()

        words = [i.upper() for i in parts[:num_style_words]]
        for word in parts[num_style_words:]:
            l = word.lower()
            if l.startswith('w/'):
                w = 'w/' + word[2:].title()
            # leave stuff like UPH and TV alone
            elif 'UPH' in word:
                w = word
            elif 'TV' in word:
                w = word.title().replace('Tv', 'TV')
            elif word in ('x2', 'x3', 'x4'):
                w = word
            else:
                w = word.title()
            words.append(w)
        title = ' '.join(words)

        if title != product.title:
            print title
            product.title = title
            product.save()
        else:
            print " [OK]"

        print
