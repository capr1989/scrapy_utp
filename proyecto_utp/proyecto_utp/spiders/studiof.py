import json
import base64
from urllib.parse import urlencode, urlparse, parse_qs, unquote
import scrapy
from proyecto_utp.items import ProductItem
from proyecto_utp.spiders.base import BaseSpider

class StudioFSpider(BaseSpider):
    name = "studiof"
    allowed_domains = ["studiofpanama.pa"]
    base_url = "https://www.studiofpanama.pa/_v/segment/graphql/v1"

    custom_settings = {
    'DATABASE_URL': 'mongodb://localhost:27017/ecommerce',
     
        'ITEM_PIPELINES': {
        "proyecto_utp.pipelines.database_pipeline.DatabasePipeline": 200,
        },
        'ROBOTSTXT_OBEY': False,
    }

    headers = {
        'accept': '*/*',
        'accept-language': 'es-PA,es-419;q=0.9,es;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/131.0.0.0 Safari/537.36',
    }

    def __init__(self, *args, **kwargs):
        super(StudioFSpider, self).__init__(*args, **kwargs)
        self.total_products = 0  
    def start_requests(self):
        encoded_url = (
            "https://www.studiofpanama.pa/_v/segment/graphql/v1?workspace=master&maxAge=short&appsEtag=remove"
            "&domain=store&locale=es-PA&__bindingId=cf042d2a-f3a3-4967-a406-f5ee60fc2691&operationName=productSearchV3"
            "&variables=%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A"
            "%229177ba6f883473505dc99fcf2b679a6e270af6320a157f0798b92efeab98d5d3%22%2C%22sender%22%3A%22vtex.store-resources%400.x"
            "%22%2C%22provider%22%3A%22vtex.search-graphql%400.x%22%7D%2C%22variables%22%3A%22eyJoaWRlVW5hdmFpbGFibGVJdGVtcyI6ZmFsc2UsInNrdXNGaWx0ZXIiOiJBTExfQVZBSUxBQkxFIiwic2ltdWxhdGlvbkJlaGF2aW9yIjoiZGVmYXVsdCIsImluc3RhbGxtZW50Q3JpdGVyaWEiOiJNQVhfV0lUSE9VVF9JTlRFUkVTVCIsInByb2R1Y3RPcmlnaW5WdGV4IjpmYWxzZSwibWFwIjoiYyIsInF1ZXJ5Ijoicm9wYSIsIm9yZGVyQnkiOiJPcmRlckJ5UmVsZWFzZURhdGVERVNDIiwiZnJvbSI6NTAsInRvIjo5OSwic2VsZWN0ZWRGYWNldHMiOlt7ImtleSI6ImMiLCJ2YWx1ZSI6InJvcGEifV0sIm9wZXJhdG9yIjoiYW5kIiwiZnV6enkiOiIwIiwic2VhcmNoU3RhdGUiOm51bGwsImZhY2V0c0JlaGF2aW9yIjoiU3RhdGljIiwiY2F0ZWdvcnlUcmVlQmVoYXZpb3IiOiJkZWZhdWx0Iiwid2l0aEZhY2V0cyI6ZmFsc2UsImFkdmVydGlzZW1lbnRPcHRpb25zIjp7InNob3dTcG9uc29yZWQiOnRydWUsInNwb25zb3JlZENvdW50IjozLCJhZHZlcnRpc2VtZW50UGxhY2VtZW50IjoidG9wX3NlYXJjaCIsInJlcGVhdFNwb25zb3JlZFByb2R1Y3RzIjp0cnVlfX0%3D%22%7D"
        )

        decoded_url, parsed_url, query_params = self.decode_url(encoded_url)
        extensions_json, decoded_variables = self.extract_and_decode_variables(query_params)

        initial_pagination = (0, 49) 
        modified_variables = self.modify_variables(
            decoded_variables,
            hide_unavailable=True,
            order_by="OrderByTopSaleDESC",
            pagination=initial_pagination
        )

        modified_url = self.encode_modified_url(parsed_url, query_params, extensions_json, modified_variables)

        self.logger.info(f"Starting request with URL: {modified_url}")
        yield scrapy.Request(
            modified_url, 
            headers=self.headers, 
            callback=self.parse_page, 
            meta={'pagination': initial_pagination}
        )

    def parse_page(self, response):
        self.logger.info(f"Parsing page: {response.url}")
        try:
            data = response.json().get('data', {})
            products = data.get('productSearch', {}).get('products', [])
            product_length = len(products)

            self.logger.info(f"Retrieved {product_length} products from current page.")

            for product in products:
                link = product.get('link')
                sku = product.get('productReference')

                if not link or not sku:
                    self.logger.warning(f"Missing 'link' or 'productReference' in product: {product}")
                    continue  

                yield from self.get_raw_response(product, ProductItem, store="Studio F", what_is_it="Product", sku=sku , response_url=f"https://www.studiofpanama.pa{link}", country = 'Panama')


            # Increment the total products counter
            self.total_products += 1
            self.logger.debug(f"Product scraped: {self.total_products} | URL: {link}")

            # Pagination logic
            if product_length == 50:  
                current_from, current_to = response.meta['pagination']
                new_from = current_to + 1
                new_to = new_from + 49  
                new_pagination = (new_from, new_to)

                decoded_url, parsed_url, query_params = self.decode_url(response.url)
                extensions_json, decoded_variables = self.extract_and_decode_variables(query_params)

                modified_variables = self.modify_variables(decoded_variables, pagination=new_pagination)
                modified_url = self.encode_modified_url(parsed_url, query_params, extensions_json, modified_variables)

                self.logger.info(f"Fetching next page with URL: {modified_url}")
                yield scrapy.Request(
                    modified_url, 
                    headers=self.headers, 
                    callback=self.parse_page, 
                    meta={'pagination': new_pagination}
                )
            else:
                self.logger.info("No more products available. Pagination complete.")

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON from {response.url}: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")

    def spider_closed(self, spider):
        self.logger.info(f"Spider closed: {spider.name}")
        self.logger.info(f"Total products scraped: {self.total_products}")

    @staticmethod
    def decode_url(encoded_url):
        decoded_url = unquote(encoded_url)
        parsed_url = urlparse(decoded_url)
        query_params = parse_qs(parsed_url.query)
        return decoded_url, parsed_url, query_params

    @staticmethod
    def extract_and_decode_variables(query_params):
        encoded_extensions = query_params['extensions'][0]
        extensions_json = json.loads(encoded_extensions)
        base64_variables = extensions_json.get('variables', '')
        decoded_variables = json.loads(base64.b64decode(base64_variables).decode('utf-8'))
        return extensions_json, decoded_variables

    @staticmethod
    def modify_variables(decoded_variables, hide_unavailable=None, order_by=None, pagination=None):
        if hide_unavailable is not None:
            decoded_variables["hideUnavailableItems"] = hide_unavailable
        if order_by:
            decoded_variables["orderBy"] = order_by
        if pagination:
            decoded_variables["from"], decoded_variables["to"] = pagination
        return decoded_variables

    @staticmethod
    def encode_modified_url(parsed_url, query_params, extensions_json, modified_variables):
        modified_variables_base64 = base64.b64encode(json.dumps(modified_variables).encode('utf-8')).decode()
        extensions_json['variables'] = modified_variables_base64
        query_params['extensions'] = [json.dumps(extensions_json)]

        encoded_query = urlencode(query_params, doseq=True)
        modified_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{encoded_query}"
        return modified_url
