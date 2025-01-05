
from mongoengine import connect, disconnect
from proyecto_utp.pipelines.base_pipeline import BasePipeline
from proyecto_utp.pipelines.product_item_handler import ProductItemHandler
from proyecto_utp.pipelines.stock_item_handler import StockItemHandler
import logging

logger = logging.getLogger(__name__)

class DatabasePipeline(BasePipeline):
    def __init__(self, database_url):
        super().__init__(database_url)
        self.product_handler = None
        self.stock_handler = None
        self.use_product_buffer = True 
        self.use_stock_buffer = True    

    def open_spider(self, spider):
        try:
            self.use_product_buffer = getattr(spider, 'use_product_buffer', self.use_product_buffer)
            self.use_stock_buffer = getattr(spider, 'use_stock_buffer', self.use_stock_buffer)

            connect(host=self.database_url, alias='default')

            self.product_handler = ProductItemHandler(use_buffer=self.use_product_buffer)
            self.stock_handler = StockItemHandler(use_buffer=self.use_stock_buffer)

            logger.info(f"{spider.name}: Database connection initialized with "
                        f"Product Buffering: {self.use_product_buffer}, "
                        f"Stock Buffering: {self.use_stock_buffer}.")
        except Exception as e:
            logger.error(f"{spider.name}: Failed to initialize database connection: {e}")
            raise e

    def close_spider(self, spider):
        try:
            if self.product_handler:
                self.product_handler.flush()
            if self.stock_handler:
                self.stock_handler.flush()
            disconnect(alias='default')
            logger.info(f"{spider.name}: Database connection closed.")
        except Exception as e:
            logger.error(f"{spider.name}: Error during spider closure: {e}")

    def process_item(self, item, spider):
        try:
            if 'productitem' in item:
                self.product_handler.add_item(item['productitem'])
            elif 'stockitem' in item:
                self.stock_handler.add_item(item['stockitem'])
            else:
                logger.warning(f"{spider.name}: Unknown item type: {item}")
            return item
        except Exception as e:
            logger.error(f"{spider.name}: Error processing item: {e}")
            raise e
