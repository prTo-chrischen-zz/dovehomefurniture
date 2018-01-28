import json
import re
from urllib2 import urlopen
from bs4 import BeautifulSoup
from pprint import pprint


spConfig_regex = re.compile(r'\((.+)\)')

def get_soup(url):
    page = urlopen(url)
    print url
    return BeautifulSoup(page, 'html.parser')

soup = get_soup('http://www.modusfurniture.com/products/categories.html')

data = {}
items = soup.find_all('li', attrs={'class': 'item-product'})
for item in items:
    a = item.find('a')
    url = a['href']

    img = item.find('img')
    image = img['src']

    name = item.find('span', attrs={'class': 'name'}).text.strip()

    data[name] = {'url': url, 'image': image, 'subcategories': {}}


for category, cat_data in data.iteritems():
    cat_soup = get_soup(cat_data['url'])

    items = cat_soup.find_all('li', attrs={'class': 'item-product'})

    for item in items:
        a = item.find('a')
        url = a['href']

        img = item.find('img')
        image = img['src']

        name = item.find('span', attrs={'class': 'name'}).text.strip()

        subcat_data = {
            'url': url,
            'image': image,
            'products': {}
        }
        cat_data['subcategories'][name] = subcat_data

        subcat_soup = get_soup(url)
        prod_items = subcat_soup.find_all('li', attrs={'class': 'item'})
        for prod_item in prod_items:
            a = prod_item.find('a')
            url = a['href']

            img = prod_item.find('img')
            image = img['src']

            name = prod_item.find('h2', attrs={'class': 'product-name'}).text.strip()

            product_data = {
                'url': url,
                'thumbnail': image,
                'options': {},
            }
            subcat_data['products'][name] = product_data

            # go to the product page and grab the shit
            prod_soup = get_soup(url)

            # description
            desc_div = prod_soup.find('div', attrs={'class': 'std description'})
            rows = desc_div.find_all('div', attrs={'class': 'row'})
            description = '\n'.join([row.text for row in rows])
            product_data['description'] = description

            # images
            images = []
            img_gallery_div = prod_soup.find('div', attrs={'class': 'product-image-gallery'})
            for img in img_gallery_div.find_all('img'):
                images.append(img['src'])
            product_data['images'] = images

            # SKUs and dimensions, for products with size options
            all_scripts = prod_soup.find_all('script', attrs={'type': 'text/javascript'})
            scripts = [s for s in all_scripts if 'var simpleProducts' in s.text]
            if scripts:
                script = scripts[0]
                code_line = [line for line in script.text.split('\n')
                             if 'simpleProducts' in line][0]
                js_str = code_line.split('=')[1].rsplit(',', 1)[0].replace('\\\\', '\\')
                options = json.loads(js_str)

                # cross reference these with spConfig, so that we know what the
                # names are for these things
                config_script = [s for s in all_scripts if 'var spConfig =' in s.text][0]
                code_line = [line for line in config_script.text.split('\n')
                             if 'spConfig' in line][0]
                match = spConfig_regex.search(code_line)
                js_str = match.group(1)
                stuff = json.loads(js_str)
                ref_list = stuff['attributes'].values()[0]['options']

                for idx, option in options.iteritems():
                    sku = option['sku']

                    # use spConfig to find the name
                    ref_info = [i for i in ref_list if idx in i['products']]
                    option_name = ref_info[0]['label']

                    option_data = {
                        'sku': sku,
                        'name': option_name,
                        'dimensions': option['dimensions'],
                        'price': option['price'],
                        'weight': option['weight'],
                    }
                    product_data['options'][option_name] = option_data
            else:
                # dimensions
                div = prod_soup.find('div', attrs={'id': 'productAttributes'})
                p = div.find('p', attrs={'class': 'attr_dimensions'})
                span = p.find('span', attrs={'class': 'info'})
                dimensions = span.text
                product_data['dimensions'] = dimensions

                # weight
                p = div.find('p', attrs={'class': 'attr_weight'})
                span = p.find('span', attrs={'class': 'info'})
                weight = span.text
                product_data['weight'] = weight

                # sku
                span = prod_soup.find('span', attrs={'id': 'sku'})
                sku = span.text.replace('SKU ', '')
                product_data['sku'] = sku

with open('dump.json', 'w') as f:
    json.dump(data, f)
