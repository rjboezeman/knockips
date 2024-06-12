from utils.logger import log

class IPSetManager(KnockIPBase):
    def __init__(self):
        try:
            self.signup()
        except FileNotFoundError:
            log.error("Error: GeoIP database file not found. Exiting...")
            exit(1)
    
    async def process_log_line(log_line):
        pass
