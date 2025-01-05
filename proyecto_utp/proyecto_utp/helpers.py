import json
import logging
from bs4 import BeautifulSoup
from scrapy.http import HtmlResponse


logger = logging.getLogger(__name__)

def get_schema_json(response):
  
    if not isinstance(response, str):
        try:
            schema_data = response.xpath("//script[@type='application/ld+json']/text()").get()

            if not schema_data:
                logger.warning(f"No schema data found in {response.url}")
                return None

            schema_json = json.loads(schema_data)
            return schema_json

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse schema JSON in {response.url}: {e}")
            return None
        except AttributeError as e:
            logger.error(f"Response object does not have an expected structure: {e}")
            return None

    try:
        schema_data = BeautifulSoup(response, 'html.parser').find("script", {"type": "application/ld+json"}).string
        if not schema_data:
            logger.warning("No schema data found in raw HTML.")
            return None

        schema_json = json.loads(schema_data)
        return schema_json

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse schema JSON from raw HTML: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error processing schema from raw HTML: {e}")
        return None
    


def extract_magento_config( response):
  
    data_html_tags = response.css("script[type='text/x-magento-init']::text").getall()
    for tag in data_html_tags:
        try:
            data = json.loads(tag)
            magento_swatch_data = data.get("[data-role=swatch-options]", {}).get('Magento_Swatches/js/swatch-renderer', {})
            if magento_swatch_data:
                json_config = magento_swatch_data.get('jsonConfig', {})
                json_swatch_config = magento_swatch_data.get('jsonSwatchConfig', {})
                return {
                    'jsonConfig': json_config,
                    'jsonSwatchConfig': json_swatch_config
                }
        except json.JSONDecodeError:
            logger.error(f"Failed to parse Magento JSON in {response.url}")
    return None



def extract_categories(html_content, url):
    
    response = convert_to_html_response(url, html_content)
    
    categories = response.css("div.breadcrumbs a::text").getall()
    
    cleaned_categories = [cat.strip() for cat in categories[1:]]
    
    return cleaned_categories

def extract_price_from_raw_price(value):
 
    if isinstance(value, dict) and 'amount' in value:
        try:
            return float(value['amount'])
        except (TypeError, ValueError):
            logger.warning(f"Invalid amount in price data: {value}")
    return None


def convert_to_html_response(url, html_content, encoding='utf-8'):
  
    return HtmlResponse(
        url=url,
        body=html_content.encode(encoding),  
        encoding=encoding
    )