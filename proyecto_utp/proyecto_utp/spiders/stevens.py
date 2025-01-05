
import json

from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlencode
from scrapy import FormRequest
from proyecto_utp.items import ProductItem, StockItem
from proyecto_utp.spiders.base import BaseSpider
from proyecto_utp.helpers import get_schema_json, extract_magento_config

class StevensSpider(BaseSpider):
    
    name = "stevens"
    allowed_domains = ["stevens.com.pa"]
    start_urls = ["https://stevens.com.pa/dama/"]
    custom_settings = {
        'DATABASE_URL': 'mongodb://localhost:27017/ecommerce',
         'ITEM_PIPELINES': {
            "proyecto_utp.pipelines.database_pipeline.DatabasePipeline": 200,
           },
    }
    
    use_product_buffer = False  
    use_stock_buffer = True     

    rules = (
        Rule(
            LinkExtractor(
                allow=(r'dama/ropa-de-dama/', r'\?p'),
                deny=(r'accesorios', r'belleza', r'zapateria', r'infantiles', r'bebe',
                      r'regalos', r'jugueteria', r'hogar', r'muebeleria', r'fragancias',
                      r'otras-categorias', r'otras categorias', r'fragancias/hombre', r'dama/accesorios',
                      r'dama/ropa-intima', r'accesorios-de-cabello', r'bisuteria', r'carteras',
                      r'dama/accesorios/otros-accesorios', r'ropa-interior', r'caballero/accesorios',
                      r'lentes', r'relojes', r'sombreros', r'otros-accesorios'),
                restrict_css=('div.navigation-container', 'div.pages ul.items.pages-items'),
                unique=True
            ),
            follow=True,
        ),
        Rule(
            LinkExtractor(
                allow=(r'/.*-e\d+\.html',),
                deny=(r'accesorios', r'belleza', r'zapateria', r'infantiles', r'bebe',
                      r'regalos', r'jugueteria', r'hogar', r'muebeleria', r'fragancias',
                      r'otras-categorias', r'otras categorias', r'fragancias/hombre', r'dama/accesorios',
                      r'dama/ropa-intima', r'accesorios-de-cabello', r'bisuteria', r'carteras',
                      r'dama/accesorios/otros-accesorios', r'ropa-interior', r'caballero/accesorios',
                      r'lentes', r'relojes', r'sombreros', r'otros-accesorios'),
                unique=True
            ),
            callback='parse_item',
            follow=False,
        ),
    )

    def parse_item(self, response):
        self.logger.info(f"Received response from {response.url} with status {response.status}")

        try:
            schema_json = get_schema_json(response)
            if not schema_json:
                self.logger.warning(f"No valid schema JSON found in {response.url}")
                return

            sku = schema_json.get("sku", "")
            self.logger.info(f"Extracted SKU: {sku}")

        except Exception as e:
            self.logger.error(f"Unexpected error parsing schema JSON in {response.url}: {e}")
            return

        yield from self.get_raw_response(response.text, ProductItem, store="Stevens", what_is_it="Product", sku=sku , response_url=response.url, country='Panamá')


        magento_config = extract_magento_config(response)
        if not magento_config:
            self.logger.warning(f"No Magento configuration found in {response.url}")
            return

        json_config = magento_config.get('jsonConfig', {})
        colors = json_config.get('attributes', {}).get('277', {}).get('options', [])
        sizes = json_config.get('attributes', {}).get('617', {}).get('options', [])

        # Generate stock requests
        for color in colors:
            for size in sizes:
                stock_payload = {
                    'sku': sku,
                    'options[277]': color['id'],
                    'options[617]': size['id']
                }
                stock_encoded = urlencode(stock_payload)

                yield FormRequest(
                    url='https://stevens.com.pa/products/index/productstock',
                    method='POST',
                    headers={
                        'accept': '*/*',
                        'accept-language': 'es-PA,es-419;q=0.9,es;q=0.8,en;q=0.7',
                        'cache-control': 'no-cache',
                        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'origin': 'https://stevens.com.pa',
                        'referer': response.url,
                        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                        'x-requested-with': 'XMLHttpRequest'
                    },
                    body=stock_encoded,
                    callback=self.parse_stock,
                    meta={
                        'sku': sku,
                        'color_id': color['id'],
                        'color_label': color['label'].strip(),
                        'size_id': size['id'],
                        'size_label': size['label'].strip(),
                    },
                    dont_filter=True
                )

    def parse_stock(self, response):
        # Extract metadata
        sku = response.meta.get('sku')
        color_id = response.meta.get('color_id')
        color_label = response.meta.get('color_label')
        size_id = response.meta.get('size_id')
        size_label = response.meta.get('size_label')

        self.logger.info(f"Stock response for SKU {sku}, Color ID {color_id}, Size ID {size_id}")

        try:
            stock_data = json.loads(response.text)
    
            yield from self.get_raw_response(
                    stock_data, 
                    StockItem, 
                    store="Stevens", 
                    what_is_it="Stock",   
                    variant_id = f"{sku}-{color_label}-{size_label}",
                    sku=sku,
                    color_id=color_id,
                    color_label=color_label,
                    size_id=size_id,
                    size_label=size_label,
                    country='Panamá'
                    )

        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse stock data for SKU {sku} at {response.url}")
