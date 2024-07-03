from utils.knockIPBase import KnockIPBase
from utils.logger import log
import re



class FirewallLogger(KnockIPBase):
    async def process_log_line(self, log_line):
        log.debug('FirewallLogger process_log_line: ' + log_line)
        # Define the regular expression pattern to extract the required fields
        pattern = (
            r'SRC=(?P<source_IP>\d{1,3}(?:\.\d{1,3}){3}) '
            r'DST=(?P<dest_IP>\d{1,3}(?:\.\d{1,3}){3}) '
            r'.* PROTO=(?P<protocol>\w+) '
            r'SPT=(?P<source_PORT>\d+) '
            r'DPT=(?P<target_PORT>\d+)'
        )
        
        # Search the pattern in the log line
        match = re.search(pattern, log_line)
        
        # If a match is found, return the extracted fields as a dictionary
        if match:
            output = match.groupdict()
            output['country'] = self.get_country_by_ip(output['source_IP'])
            output['city'] = self.get_city_by_ip(output['source_IP'])
            output['asn'] = self.get_asn_by_ip(output['source_IP'])
            output['organization'] = self.get_asn_organization_by_ip(output['source_IP'])
            return output
        else:
            return None
        
    async def take_action(self, output):
        log.debug(f"FirewallLogger take_action: Country: {output['country']}, City: {output['city']}, Source IP: {output['source_IP']}, Destination IP: {output['dest_IP']}, Source Port: {output['source_PORT']}, Destination Port: {output['target_PORT']}")

    async def cleanup(self):
        log.debug('FirewallLogger cleanup')