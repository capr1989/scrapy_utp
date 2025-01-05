from abc import ABC, abstractmethod
import logging
from proyecto_utp.pipelines.buffer_manager import BufferManager

logger = logging.getLogger(__name__)

class ItemHandler(ABC):
    def __init__(self, collection, buffer_size=100, operation_generator=None, use_buffer=True):
        self.use_buffer = use_buffer
        self.buffer_manager = None

        if self.use_buffer:
            self.buffer_manager = BufferManager(
                collection=collection,
                buffer_size=buffer_size,
                operation_generator=operation_generator
            )
        else:
            self.collection = collection
            self.operation_generator = operation_generator

    def add_item(self, item):
        if self.use_buffer:
            self.buffer_manager.add(item)
        else:
            self.process_immediately(item)

    def flush(self):
    
        if self.use_buffer and self.buffer_manager:
            self.buffer_manager.flush()

    @abstractmethod
    def process_immediately(self, item):
        pass
