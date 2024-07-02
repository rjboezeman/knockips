from utils.logger import log
from utils.knockIPBase import KnockIPBase
from pyroute2 import IPSet
from config import ipset_goodguys, ipset_badguys, knock_sequence
from pyroute2.netlink.exceptions import NetlinkError
import asyncio
from datetime import datetime

class IPSetManager(KnockIPBase):
    
    def __init__(self, multi_queue, shutdown_event):
        super().__init__(multi_queue, shutdown_event)
        self.check_interval = 10 # in seconds
        self.counter = 0
        self.time_window = 60 # in seconds
        try:
            self.ipset = IPSet()
        except Exception as e:
            log.error(f"Could not initialize IPSet: {e}")
            self.port_knocking_enabled = False
        self.knockers = {}
        
        self.permanent_goodguys_list = []
        self.permanent_badguys_list = []
        self.temporary_goodguys_list = []
        self.temporary_badguys_list = []

        self.port_knocking_enabled = True

    def extract_ip_addresses(self, ipset_data):
        ip_addresses = []

        def recursive_extract(attrs):
            for attr in attrs:
                if attr[0] == 'IPSET_ATTR_IP_FROM':
                    for ip_attr in attr[1]['attrs']:
                        if ip_attr[0] == 'IPSET_ATTR_IPADDR_IPV4':
                            ip_addresses.append(ip_attr[1])
                elif isinstance(attr[1], dict) and 'attrs' in attr[1]:
                    recursive_extract(attr[1]['attrs'])

        for i in ipset_data:
            recursive_extract(i['attrs'])
        return ip_addresses

    async def process_log_line(self, log_line):
        log.debug('IPSetManager process_log_line: ' + log_line)
        return True
    
    async def update_ipsets(self):
        while not self.shutdown_event.is_set():
            try:
                if self.counter < self.check_interval:
                    self.counter += 1
                    await asyncio.sleep(1)
                else:
                    self.counter = 0
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    for item in self.temporary_goodguys_list:
                        log.debug(f"Processing IP address: {item[0]}, timestamp: {item[1]}")
                        # change the if statement to already remove the item from the list if the timestamp is older than 1 minute:
                        total_seconds = int((datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") - datetime.strptime(item[1], "%Y-%m-%d %H:%M:%S")).total_seconds())
                        log.debug(f"Total seconds remaining in time window: {self.time_window - total_seconds}")
                        if total_seconds > self.time_window:
                            try:
                                self.ipset.delete(ipset_goodguys, item[0])
                                self.temporary_goodguys_list.remove(item)
                                log.info(f"Time window closed ({total_seconds} seconds) for IP address {item[0]}, it has been removed from ipset '{ipset_goodguys}'.")
                            except NetlinkError as e:
                                log.error(f"Error: IP address {item[0]} could not be removed from ipset '{ipset_goodguys}': {e}.")
                            except Exception as e:
                                log.error(f"Unknown error: {e}")                
            except Exception as e:
                log.error(f"Error: Could not update ipsets: {e}")
                self.port_knocking_enabled = False

    async def add_to_ipset(self, ipset_name, ip_address):
        try:
            self.ipset.add(ipset_name, ip_address)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.temporary_goodguys_list.append([ip_address, timestamp])
            log.info(f"IP address {ip_address} has been added to ipset '{ipset_name}'.")
        except NetlinkError as e:
            log.error(f"Error: IP address {ip_address} could not be added to ipset '{ipset_name}': {e}.")
        except Exception as e:
            log.error(f"Unknown error: {e}")

    async def take_action(self, output):
        log.debug(f"IPSetManager take_action: {output}")
        log.debug(f"Knockers: {self.knockers}")
        source_ip = output['source_IP']
        target_port = output['target_PORT']
        if self.port_knocking_enabled == False:
            log.info(f"source_IP: {source_ip}, target_PORT: {target_port}  # (Port knocking disabled, ipsets not found)")
            return
        knock_count = self.knockers.get(source_ip, {}).get('knock_count', 0)

        if source_ip in self.knockers:
            if target_port == str(knock_sequence[knock_count]):
                log.info(f"Knocker {source_ip} has CONTINUED to knock on TCP port {target_port} with knock count: {knock_count}.")
                self.knockers[source_ip]['knock_count'] += 1
                if self.knockers[source_ip]['knock_count'] == len(knock_sequence):
                    log.info(f"Knocker {source_ip} has completed the knock sequence.")
                    self.knockers[source_ip]['knock_count'] = 0
                    await self.add_to_ipset(ipset_goodguys, source_ip)
            else:
                log.info(f"Knocker {source_ip} has FAILED the knock sequence at count: {knock_count}.")
                del self.knockers[source_ip]
        elif target_port == str(knock_sequence[0]):
            log.info(f"Knocker {source_ip} has STARTED the knock sequence.")
            self.knockers[source_ip] = {'knock_count': 1}
        else:
            log.info(f"Knocker {source_ip} has failed the knock sequence on TCP port {target_port}.")


    async def run(self):
        log.debug("IPSetManager run")
        try:
            self.ipset = IPSet()
            asyncio.create_task(self.update_ipsets())
            self.all_ipset = self.ipset.list()
            self.ipset_list = [j[1] for i in self.all_ipset for j in i['attrs'] if j[0] == 'IPSET_ATTR_SETNAME']
            if((ipset_goodguys not in self.ipset_list) or (ipset_badguys not in self.ipset_list)):
                log.error(f"Error: ipset '{ipset_goodguys}' and/or '{ipset_badguys}' not found in list of ipsets {self.ipset_list}. Skipping ipset actions.")
                self.port_knocking_enabled = False
            else:
                self.permanent_goodguys_list = self.extract_ip_addresses(self.ipset.list(ipset_goodguys))
                self.permanent_badguys_list = self.extract_ip_addresses(self.ipset.list(ipset_badguys))
                log.info(f"Number of permanent goodguys: {len(self.permanent_goodguys_list)}")
                log.info(f"Number of permanent badguys: {len(self.permanent_badguys_list)}")
                log.info(f"Knock sequence: {knock_sequence}")
        except Exception as e:
            log.error(f"Could not initialize IPSet: {e}")
            self.port_knocking_enabled = False
        await super().run()

    async def cleanup(self):
        log.debug("IPSetManager cleanup")
        try:
            for item in self.temporary_goodguys_list:
                log.info(f"Cleaning up temporary goodguys_list: {item}")
                self.ipset.delete(ipset_goodguys, item[0])
                self.temporary_goodguys_list.remove(item)
                log.info(f"IP address {item[0]} has been removed from ipset '{ipset_goodguys}'.")
        except NetlinkError as e:
            log.error(f"Error: IP address {item[0]} could not be removed from ipset '{ipset_goodguys}': {e}.")
        except Exception as e:
            log.error(f"Unknown error: {e}")  