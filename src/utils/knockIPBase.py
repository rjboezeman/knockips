
from abc import ABC, abstractmethod
from config import ERROR_LOG_ENTRY
from utils.geoiplookup import GeoIPLookup
from utils.multiQueue import MultiQueue
from utils.logger import log
import asyncio

class KnockIPBase(ABC):

    def __init__(self, multi_queue: MultiQueue, shutdown_event: asyncio.Event):
        log.debug(f"Initializing {self.__class__.__name__}")
        self.multi_queue = multi_queue
        self.shutdown_event = shutdown_event
        self.geo_ip_lookup = None
        self.log_processor = None
        self.geo_ip_lookup = GeoIPLookup()
        self.queue = None

    async def put(self, item):
        await self.multi_queue.put(item)

    async def get(self):
        return await self.multi_queue.get(self.queue)

    def signup(self):
        self.queue = self.multi_queue.signup()

    def signout(self):
        if self.queue:
            self.multi_queue.signout(self.queue)
        self.queue = None

    def is_shutting_down(self):
        return self.shutdown_event.is_set()
    
    def set_log_processor(self, log_processor):
        self.log_processor = log_processor

    async def do_shutdown(self):
        await self.put(ERROR_LOG_ENTRY)
        self.shutdown_event.set()
    
    # override this function in child class if needed.
    async def run(self):
        self.signup()
        while not self.shutdown_event.is_set() or not self.multi_queue.empty(queue):
            log_line = await self.multi_queue.get(self.queue) # with peek we don't actually remove the item from the queue
            if log_line == ERROR_LOG_ENTRY:
                log.error(f"Received error signal ({self.__class__.__name__}), shutting down...")
                self.shutdown_event.set()
                break
            if self.log_processor:
                log.debug(f"{self.__class__.__name__} process_log_line: calling processor of {self.log_processor.__class__.__name__} with: {log_line}")
                output = await self.log_processor.process_log_line(log_line)
            else:
                output = await self.process_log_line(log_line)
            if output:
                await self.take_action(output)
            else:
                log.error(f"Failed to process log line ({self.__class__.__name__}): {log_line}")
        self.signout()
        await self.cleanup()
    
    def get_country_by_ip(self, ip):
        if not self.geo_ip_lookup:
            log.debug('GeoIP lookup of country not available.')
            return None
        return self.geo_ip_lookup.get_country_by_ip(ip)

    def get_city_by_ip(self, ip):
        if not self.geo_ip_lookup:
            log.debug('GeoIP lookup of city not available.')
            return None
        return self.geo_ip_lookup.get_city_by_ip(ip)
    
    def get_asn_by_ip(self, ip):
        if not self.geo_ip_lookup:
            log.debug('GeoIP lookup of ASN not available.')
            return None
        return self.geo_ip_lookup.get_asn_by_ip(ip)

    def get_asn_organization_by_ip(self, ip):
        if not self.geo_ip_lookup:
            log.debug('GeoIP lookup of ASN organization not available.')
            return None
        return self.geo_ip_lookup.get_asn_organization_by_ip(ip)

    @abstractmethod
    async def process_log_line(self):
        pass

    @abstractmethod
    async def take_action(self):
        pass

    @abstractmethod
    async def cleanup(self):
        pass
