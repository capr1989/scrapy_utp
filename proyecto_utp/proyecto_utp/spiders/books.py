from proyecto_utp.spiders.base import BaseSpider
from proyecto_utp.items import ProductItem
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

class BooksSpider(BaseSpider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/index.html"]
    
    custom_settings = {
    'DATABASE_URL': 'mongodb://localhost:27017/ecommerce',
   
        'ITEM_PIPELINES': {
        "proyecto_utp.pipelines.database_pipeline.DatabasePipeline": 200,
        },
}


    rules = (
    Rule(
        LinkExtractor(
            allow=(
                r'.*',
                
            ),
          
            restrict_css=('li.next', 'ol.row'),
            unique=True, 

        ),
        follow=True,
    ),
     Rule(
            LinkExtractor(
                allow=(  r'.*'),
                unique=True
            ),
            callback='parse',
            follow=False,
        ),
    
    )

    def parse(self, response):
        
        self.logger.info(f"!Response from {response.url}")

        yield from self.get_raw_response(response.text, ProductItem, store="Books", what_is_it="Book", sku="1234", response_url=response.url, country='USA')
        