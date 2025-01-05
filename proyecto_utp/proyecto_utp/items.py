
from scrapy import Item, Field
from itemloaders.processors import TakeFirst, MapCompose

class BaseResponseItem(Item):
    response_text = Field(output_processor=TakeFirst())  
    store = Field(output_processor=TakeFirst())
    country = Field(output_processor=TakeFirst())
    what_is_it = Field(output_processor=TakeFirst())
    

# Item for Product Details
class ProductItem(BaseResponseItem):
    sku = Field(output_processor=TakeFirst())
    response_url = Field(output_processor=TakeFirst())
    
class StockItem(BaseResponseItem):
    variant_id = Field(output_processor=TakeFirst())
    sku = Field(output_processor=TakeFirst())
    color_id = Field(output_processor=TakeFirst())
    color_label = Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))
    size_id = Field(output_processor=TakeFirst())
    size_label = Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))
