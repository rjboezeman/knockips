
from abc import ABC, abstractmethod
from config import ERROR_LOG_ENTRY
from utils.geoiplookup import GeoIPLookup
from utils.multiQueue import MultiQueue
from utils.logger import log
import asyncio

class KnockIPBase(ABC):

    def __init__(self, multi_queue: MultiQueue, shutdown_event: asyncio.Event):
        self.multi_queue = multi_queue
        self.queue = multi_queue.signup()
        self.shutdown_event = shutdown_event
        self.geo_ip_lookup = GeoIPLookup()


    async def put(self, item):
        await self.multi_queue.put(item)

    async def get(self):
        item = await self.multi_queue.get(self.queue)
        if self.log_processor:
            return self.log_processor.process_log_line(item)
        else:
            return item

    def signup(self):
        pass

    def signout(self):
        self.multi_queue.signout(self.queue)

    def is_shutting_down(self):
        return self.shutdown_event.is_set()
    
    def set_log_processor(self, log_processor):
        self.log_processor = log_processor

    async def do_shutdown(self):
        await self.put(ERROR_LOG_ENTRY)
        self.shutdown_event.set()
    
    # override this function in child class if needed.
    async def run(self):
        while not self.shutdown_event.is_set() or not self.multi_queue.empty(queue):
            log_line = await self.multi_queue.get(self.queue) # with peek we don't actually remove the item from the queue
            if log_line == ERROR_LOG_ENTRY:
                log.error("Received error signal, shutting down...")
                self.shutdown_event.set()
                break
            processed_successfully = self.process_log_line(log_line)
            if processed_successfully:
                pass
            else:
                log.error(f"Failed to parse log line: {log_line}")
    
    @abstractmethod
    async def process_log_line(self):
        pass
