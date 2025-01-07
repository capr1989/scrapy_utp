from proyecto_utp.spiders.base import BaseSpider
from proyecto_utp.spiders.mixins import PaginationMixin
from proyecto_utp.items import ProductItem
from urllib.parse import urlencode
import scrapy
import json 

class TommySpider(BaseSpider, PaginationMixin):
    base_url = "https://pa.tommy.com/buscapagina?fq=specificationFilter_19%3aMujer&fq=C%3a%2f14%2f&fq=B%3a2000000&O=OrderByScoreDESC&PS=12&sl=674bdea2-21db-43d7-94ba-b10e760a4a88&cc=12&sm=0"
    name = "tommy"
    allowed_domains = ["pa.tommy.com"]
    processed_ids = set()  # Use a set to track unique product IDs
    custom_settings = {
        'DATABASE_URL': 'mongodb://localhost:27017/ecommerce',
         'ITEM_PIPELINES': {
            "proyecto_utp.pipelines.database_pipeline.DatabasePipeline": 200,
           },
    }
    
    def start_requests(self):
        # Start with page 1
        params = {
            "PageNumber": 1,  # Starting page
        }
        url = f"{self.base_url}&{urlencode(params)}"
        self.logger.info(f"Starting requests with URL: {url}")
        yield scrapy.Request(url, callback=self.parse_page, meta={"params": params})

    def parse_page(self, response):
        # Extract items from the page
        product_selectors = response.css('body > div > ul > li > div.product-item__wrapper > div > figure > a')
        extracted_items = []
        for product in product_selectors:
            product_id = product.attrib.get("data-id")
            href = product.attrib.get("href")
            if not product_id:
                self.logger.warning("No product ID found in the current selector.")
                continue
            
            if product_id in self.processed_ids:
                self.logger.info(f"Duplicate product ID {product_id} skipped.")
                continue  # Skip already processed product IDs
            
            self.processed_ids.add(product_id)  # Add to the set of processed IDs
            
            # Send request to product details endpoint
            yield response.follow(
                f'https://pa.tommy.com/api/catalog_system/pub/products/variations/{product_id}', 
                callback=self.parse_next,
                meta={"product_id": product_id, 'href': href}  # Pass product ID for logging
            )
            self.logger.info(f"Queued product ID: {product_id} for processing.")
            extracted_items.append(product_id)

        # Dynamically calculate the limit based on the length of extracted items
        limit = len(extracted_items)
        self.logger.info(f"Extracted {limit} items on this page.")


        if limit:
            yield from self.handle_pagination(
                response=response,
                params_key="PageNumber",
                items=extracted_items,
                callback= self.parse_page
            )
        else:
            self.logger.info("No more items to fetch. Pagination complete.")

    def parse_next(self, response):
        product_id = response.meta.get("product_id", "Unknown ID")
        
        href = response.meta.get("href", "Unknown href")

        
        self.logger.info(f"Processed product ID: {product_id}. Total unique products processed: {len(self.processed_ids)}")
        product = json.loads(response.text)
        yield from self.get_raw_response(product, ProductItem, response_url = href, sku= product_id,  store="Tommy Hilfiger", what_is_it="Product", country = 'Panama')