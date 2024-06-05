import json
import asyncio

# Load configuration from JSON file
# Reading configuration
try:
    with open('../config.json') as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    print("Error: Configuration file not found. Exiting...")
    exit(1)

log_queue = asyncio.Queue()
shutdown_event = asyncio.Event()

try:
    logfile = config['logfile']
    ERROR_LOG_ENTRY = config['error_log_entry']
except KeyError as e:
    print(f"Error: Missing configuration key in config.json: {e}")
    exit(1)