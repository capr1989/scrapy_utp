
import logging

logger = logging.getLogger(__name__)

class BufferManager:
    def __init__(self, collection, buffer_size=100, operation_generator=None):
     
        self.buffer = []
        self.BUFFER_SIZE = buffer_size
        self.collection = collection
        self.operation_generator = operation_generator
        self.bulk_operations_executed = 0

        if self.operation_generator:
            logger.debug("BufferManager: Operation generator set.")
        else:
            logger.warning("BufferManager: No operation generator provided during initialization.")

    def add(self, item):
    
        self.buffer.append(item)
        logger.info(f"BufferManager: Item added to buffer. Buffer size: {len(self.buffer)}")
        if len(self.buffer) >= self.BUFFER_SIZE:
            logger.info("BufferManager: Buffer size reached. Flushing buffer.")
            self.flush()

    def flush(self, operation_generator=None):
      
        if not self.buffer:
            logger.debug("BufferManager: Buffer is empty. Nothing to flush.")
            return

        # Use the provided operation_generator or the default one
        operation_generator = operation_generator or self.operation_generator

        if not operation_generator:
            logger.warning("BufferManager: No operation generator provided.")
            return

        logger.info(f"BufferManager: Using operation generator: {operation_generator}")

        try:
            operations = [operation_generator(item) for item in self.buffer]
            results = self.collection.bulk_write(operations, ordered=False)
            self.bulk_operations_executed += 1

            logger.info(
                f"BufferManager: Flushed {len(self.buffer)} items. "
                f"Inserted: {results.upserted_count}, Modified: {results.modified_count}."
            )

            self.buffer.clear()
        except Exception as e:
            logger.error(f"BufferManager: Failed to flush buffer: {e}")
