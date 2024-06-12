from utils.logger import log
from utils.knockIPBase import KnockIPBase
from pyroute2 import IPSet
from config import ipset_goodguys, ipset_badguys, knock_sequence
from pyroute2.netlink.exceptions import NetlinkError

class IPSetManager(KnockIPBase):
    
    def __init__(self, multi_queue, shutdown_event):
        super().__init__(multi_queue, shutdown_event)
        self.ipset = IPSet()
        self.knockers = {}

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

    async def take_action(self, output):
        log.debug(f"IPSetManager take_action: {output}")
        log.debug(f"Knockers: {self.knockers}")
        source_ip = output['source_IP']
        target_port = output['target_PORT']
        knock_count = self.knockers.get(source_ip, {}).get('knock_count', 0)

        if source_ip in self.knockers:
            if target_port == str(knock_sequence[knock_count]):
                log.info(f"Knocker {source_ip} has CONTINUED to knock on TCP port {target_port} with knock count: {knock_count}.")
                self.knockers[source_ip]['knock_count'] += 1
                if self.knockers[source_ip]['knock_count'] == len(knock_sequence):
                    log.info(f"Knocker {source_ip} has completed the knock sequence.")
                    self.knockers[source_ip]['knock_count'] = 0
                    try:
                        self.ipset.add(ipset_goodguys, source_ip)
                        log.info(f"Knocker {source_ip} has been ADDED to ipset '{ipset_goodguys}'.")
                        del self.knockers[source_ip]
                    except NetlinkError as e:
                        log.error(f"Error: Knocker {source_ip} could not be added to ipset '{ipset_goodguys}': {e}.")
                    except Exception as e:
                        log.error(f"Unknown error: {e}")
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
        self.all_ipset = self.ipset.list()
        self.ipset_list = [j[1] for i in self.all_ipset for j in i['attrs'] if j[0] == 'IPSET_ATTR_SETNAME']
        if((ipset_goodguys not in self.ipset_list) or (ipset_badguys not in self.ipset_list)):
            log.error(f"Error: ipset '{ipset_goodguys}' and/or '{ipset_badguys}' not found in list of ipsets {self.ipset_list}. Exiting.")
            await self.do_shutdown()
            return
        self.goodguys_list = self.extract_ip_addresses(self.ipset.list(ipset_goodguys))
        self.badguys_list = self.extract_ip_addresses(self.ipset.list(ipset_badguys))
        log.info(f"Number of goodguys: {len(self.goodguys_list)}")
        log.info(f"Number of badguys: {len(self.badguys_list)}")
        log.info(f"Knock sequence: {knock_sequence}")
        await super().run()