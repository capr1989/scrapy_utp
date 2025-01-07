import logging
from urllib.parse import urlencode
import scrapy
from scrapy.exceptions import NotSupported
logger = logging.getLogger(__name__)

class PaginationMixin:
    def __init__(self, base_url=None):
        self.base_url = base_url
        

    def handle_pagination(self, response, callback,  params_key='page', items=None, limit = 0):
        params = response.meta.get(params_key, {})
        current_page = params.get(params_key, 1)
        
        separator = '&' if '?' in self.base_url else '?'
        
        try:

            if len(items) > limit:
                next_page = current_page + 1
                params[params_key] = next_page
                next_url = f"{self.base_url}{separator}{urlencode(params)}"
                logger.info(f"Fetching next page: {next_url}")
                yield scrapy.Request(
                    next_url,
                    callback=callback,
                    meta={params_key: params},
                )
            else:
                logger.info("No more pages to fetch. Pagination complete.")
        except ValueError as ve:
            logger.error(f"ValueError in PaginationMixin: {ve}")
        except NotSupported as ns:
            logger.error(f"NotSupported error in PaginationMixin: {ns}")
        except Exception as e:
            logger.error(f"Unexpected error in PaginationMixin: {e}")