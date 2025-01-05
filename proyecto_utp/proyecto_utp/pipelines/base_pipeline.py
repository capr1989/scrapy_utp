
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BasePipeline(ABC):
    def __init__(self, database_url: str):
        self.database_url = database_url

    @classmethod
    def from_crawler(cls, crawler):
        database_url = crawler.settings.get("DATABASE_URL", "mongodb://localhost:27017/ecommerce")
        pipeline = cls(database_url)
        return pipeline

    @abstractmethod
    def open_spider(self, spider):
        pass

    @abstractmethod
    def close_spider(self, spider):
        pass

    @abstractmethod
    def process_item(self, item, spider):
        pass
