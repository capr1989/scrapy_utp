import json
import scrapy
from urllib.parse import urlencode
from proyecto_utp.spiders.base import BaseSpider

from proyecto_utp.items import ProductItem



class FelixSpider(BaseSpider):
    name = "felix"
    allowed_domains = ["felix.com.pa", "rebuyengine.com"]  
    base_url = "https://felix.com.pa/collections/mujer/products.json"
    custom_settings = {
    'DATABASE_URL': 'mongodb://localhost:27017/ecommerce',
      
        'ITEM_PIPELINES': {
        "proyecto_utp.pipelines.database_pipeline.DatabasePipeline": 200,
        },
        'ROBOTSTXT_OBEY': False,  
    }

    def __init__(self, *args, **kwargs):
        super(FelixSpider, self).__init__(*args, **kwargs)
        self.total_products = 0
        self.filtered_products = 0
        self.headers = {
            'accept': '*/*',
            'accept-language': 'es-PA,es-419;q=0.9,es;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'origin': 'https://felix.com.pa',
            'pragma': 'no-cache',
            'priority': 'u=1, i',  
            'referer': 'https://felix.com.pa/',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/131.0.0.0 Safari/537.36'
        }

    def start_requests(self):
        # Start with page 1
        params = {"limit": 250, "page": 1}
        url = f"{self.base_url}?{urlencode(params)}"
        self.logger.info(f"Starting requests with URL: {url}")
        yield scrapy.Request(url, callback=self.parse_page, meta={'params': params})

    def parse_page(self, response):
        ## PRODUCT TYPES
        # Define the types to filter
        types = [type_name.upper() for type_name in ['SHORTS', 'ABRIGOS Y CARDIGANS', 'BLAZERS','BLUSAS Y TOPS','CAMISETAS','FALDAS','JEANS','PANTALONES', 'VESTIDOS']]
        self.logger.info(f"Parsing page: {response.url}")
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON from {response.url}: {e}")
            return

        # Process products
        products = data.get('products', [])
        self.total_products += len(products)  
        self.logger.info(f"Found {len(products)} products on this page.")

        for product in products:
            product_type = product.get('product_type', '').upper()
            if product_type in types:
                self.filtered_products += 1  
                self.logger.info(
                    f"Product ID: {product.get('id')}, Title: {product.get('title')}, "
                    f"Category: {product.get('product_type')}"
                )
                product_id = product.get("id")
                if not product_id:
                    self.logger.warning(f"Product '{product.get('title')}' does not have an 'id'. Skipping.")
                    continue
                yield scrapy.Request(
                    url=f'https://rebuyengine.com/api/v1/custom/id/130615?limit=1&key=8c8a6779504071e3ddce474ef3082da231d18bb2&metafields=yes&shopify_product_ids={product_id}',
                    headers=self.headers,
                    callback=self.parse_product,
                    meta={'product': product},
                    dont_filter=True  
                )

        if len(products) == 250:
            # Increment page number and fetch the next page
            params = response.meta.get('params', {})
            params['page'] = params.get('page', 1) + 1
            next_url = f"{self.base_url}?{urlencode(params)}"
            self.logger.info(f"Fetching next page: {next_url}")
            yield scrapy.Request(next_url, callback=self.parse_page, meta={'params': params})
        else:
            self.logger.info("No more pages to fetch. Pagination complete.")
            self.logger.info(f"Total products processed: {self.total_products}")
            self.logger.info(f"Total filtered products: {self.filtered_products}")

    def parse_product(self, response):

        self.logger.info(f"Processing product: {response.url}")
        product = response.meta.get('product')
        if not product:
            self.logger.warning("No product data found in meta.")
            return
        try:
            data = response.json()
            metadata = data.get('metadata', {})
            input_products = metadata.get('input_products', [])[0]
            self.logger.info(f"Input products: {input_products['id']}")
           
          
                        
            
            yield from self.get_raw_response(
                input_products, ProductItem, store="Felix B Maduro", what_is_it="Product", sku=input_products.get('id') , response_url=f'https://felix.com.pa/products/{input_products.get("handle")}', country='Panamá'
                )

            
         
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON from {response.url}: {e}")
        
 
