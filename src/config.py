import json
from json import JSONDecodeError
import asyncio
from utils.multiQueue import MultiQueue
from utils.logger import log

# Load configuration from JSON file
# Reading configuration
try:
    with open('../config.json') as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    log.error("Error: Configuration file not found. Exiting...")
    exit(1)
except JSONDecodeError:
    log.error("Error: Configuration file is not valid JSON. Exiting...")
    exit(1)

multi_queue = MultiQueue()
shutdown_event = asyncio.Event()

try:
    log_file = config['log_file']
    ERROR_LOG_ENTRY = config['error_log_entry']
    geo_ip_country_db = config['geo_ip_country_db']
    geo_ip_city_db = config['geo_ip_city_db']
except KeyError as e:
    log.error(f"Error: Missing configuration key in config.json: {e}")
    exit(1)