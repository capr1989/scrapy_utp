
from datetime import datetime, timezone
from pymongo import UpdateOne
from proyecto_utp.models import StockResponse
from proyecto_utp.pipelines.item_handler import ItemHandler
import logging

logger = logging.getLogger(__name__)

class StockItemHandler(ItemHandler):
    def __init__(self, use_buffer=True):
      
        super().__init__(
            collection=StockResponse._get_collection(),
            buffer_size=100,
            operation_generator=self.stock_operation_generator,
            use_buffer=use_buffer
        )

    def stock_operation_generator(self, stock_item):
    
        current_time = datetime.now(timezone.utc)
        return UpdateOne(
            {'variant_id': stock_item.get('variant_id')},
            {
                '$set': {
                    'sku': stock_item.get('sku'),
                    'color_id': stock_item.get('color_id'),
                    'color_label': stock_item.get('color_label'),
                    'size_id': stock_item.get('size_id'),
                    'size_label': stock_item.get('size_label'),
                    'store': stock_item.get('store'),
                    'country': stock_item.get('country'),
                    'response_text': stock_item.get('response_text'),
                    'updated_at': current_time
                },
                '$setOnInsert': {
                    'created_at': current_time
                }
            },
            upsert=True
        )

    def process_immediately(self, item):
        pass  