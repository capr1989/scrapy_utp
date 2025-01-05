
from datetime import datetime, timezone
from pymongo import UpdateOne
from proyecto_utp.models import ProductResponse
from proyecto_utp.pipelines.item_handler import ItemHandler
import logging

logger = logging.getLogger(__name__)

class ProductItemHandler(ItemHandler):
    def __init__(self, use_buffer=False):
       
        super().__init__(
            collection=ProductResponse._get_collection(),
            buffer_size=100,  
            operation_generator=self.product_operation_generator,
            use_buffer=use_buffer
        )

    def product_operation_generator(self, item):
    
        current_time = datetime.now(timezone.utc)
        return UpdateOne(
            {'response_url': item.get('response_url')},
            {
                '$set': {
                    'sku': item.get('sku'),
                    'response_text': item.get('response_text'),
                    'updated_at': current_time,
                    'store': item.get('store'),
                    'country': item.get('country'),
                    'what_is_it': item.get('what_is_it'),
                },
                '$setOnInsert': {
                    'created_at': current_time
                },
            },
            upsert=True
        )

    def process_immediately(self, item):
      
        try:
            current_time = datetime.now(timezone.utc)
            result = ProductResponse.objects(response_url=item.get('response_url')).update_one(
                set__sku=item.get('sku'),
                set__response_text=item.get('response_text'),
                set__store=item.get('store'),
                set__country = item.get('country'),
                set__what_is_it=item.get('what_is_it'),
                set__updated_at=current_time,
                set_on_insert__created_at=current_time,
                upsert=True
            )
            if result:
                logger.info(f"ProductItemHandler: Upserted ProductResponse for URL: {item.get('response_url')}")
            else:
                logger.info(f"ProductItemHandler: No changes made for ProductResponse with URL: {item.get('response_url')}")
        except Exception as e:
            logger.error(f"ProductItemHandler: Failed to process item immediately: {e}")
