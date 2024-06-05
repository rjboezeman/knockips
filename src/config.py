import json
from json import JSONDecodeError
import asyncio
from utils.multiQueue import MultiQueue

# Load configuration from JSON file
# Reading configuration
try:
    with open('../config.json') as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    print("Error: Configuration file not found. Exiting...")
    exit(1)
except JSONDecodeError:
    print("Error: Configuration file is not valid JSON. Exiting...")
    exit(1)

multiQueue = MultiQueue()
shutdown_event = asyncio.Event()

try:
    logfile = config['logfile']
    ERROR_LOG_ENTRY = config['error_log_entry']
    geo_ip_db = config['geo_ip_db']
except KeyError as e:
    print(f"Error: Missing configuration key in config.json: {e}")
    exit(1)