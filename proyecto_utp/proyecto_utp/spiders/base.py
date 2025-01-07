
from scrapy.spiders import CrawlSpider

class BaseSpider(CrawlSpider):
    def __init__(self, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)

    def get_raw_response(self, response,item_type, *args, **kwargs):
        item_to_yield = {
                item_type.__name__.lower():  
                        item_type(
                            response_text=response,
                            **kwargs
                        )
                    
                }

        yield item_to_yield
