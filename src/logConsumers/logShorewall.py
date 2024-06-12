from utils.knockIPBase import KnockIPBase
from utils.geoiplookup import GeoIPLookup
from utils.logger import log
import re



class ShorewallLogger(KnockIPBase):
    def __init__(self, multi_queue, shutdown_event):
        try:
            super().__init__(multi_queue, shutdown_event)
            self.geoDb = GeoIPLookup()
        except FileNotFoundError:
            log.error("Error: GeoIP database file not found. Exiting...")
            exit(1)

    def process_log_line(self, log_line):
        # Define the regular expression pattern to extract the required fields
        pattern = (
            r'SRC=(?P<source_IP>\d{1,3}(?:\.\d{1,3}){3}) '
            r'DST=(?P<dest_IP>\d{1,3}(?:\.\d{1,3}){3}) '
            r'.* SPT=(?P<source_PORT>\d+) '
            r'DPT=(?P<target_PORT>\d+)'
        )
        
        # Search the pattern in the log line
        match = re.search(pattern, log_line)
        
        # If a match is found, return the extracted fields as a dictionary
        if match:
            output = match.groupdict()
            output['country'] = self.geoDb.get_country_by_ip(output['source_IP'])
            output['city'] = self.geoDb.get_city_by_ip(output['source_IP'])
            return output
        else:
            return None