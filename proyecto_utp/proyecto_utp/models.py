from mongoengine import *

from datetime import datetime, timezone

class BaseModel(Document):
    id = StringField(required=True, max_length=100, primary_key=True)
    created_at = DateTimeField(default=datetime.now(timezone.utc))
    updated_at = DateTimeField(default=datetime.now(timezone.utc))
    store = StringField(required=True)
    what_is_it = StringField(required=True)
    country = StringField(required=True)
    meta = {'allow_inheritance': True, 
            'indexes': ['created_at', 'updated_at', 'store',  'what_is_it', 'country'],
            'abstract': True
            }

class ProductResponse(BaseModel):
    response_url = StringField(required=True, unique=True)  
    sku = StringField(required=True, max_length=100)
    response_text = StringField(required=True)
    
    

    meta = {

        'indexes': [
            'sku',
            'response_url',
            'store',
           
        ]
    }
    
class StockResponse(BaseModel):
        variant_id = StringField(required=True, max_length=100, unique=True)  
        sku = StringField(required=True, max_length=100)
        color_id = StringField(required=True, max_length=50)
        color_label = StringField(required=True, max_length=100)
        size_id = StringField(required=True, max_length=50)
        size_label = StringField(required=True, max_length=100)
        response_text = DictField(required=True)  

        meta = {
            'indexes': [
                'sku',
                'color_id',
                'size_id',
                'color_label',
                'size_label',
                'variant_id'
                
            ]
        }
