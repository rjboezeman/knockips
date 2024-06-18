import json
from json import JSONDecodeError
import asyncio
from utils.multiQueue import MultiQueue
import os

# Load configuration from JSON file
# Reading configuration

try:
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(current_script_dir, '../config.json')
    print(f"Loading configuration from {config_file_path}")
    with open(config_file_path) as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    print("Error: Configuration file not found. Exiting...")
    exit(1)
except JSONDecodeError:
    print("Error: Configuration file is not valid JSON. Exiting...")
    exit(1)

log_multi_queue = MultiQueue()
actor_multi_queue = MultiQueue()
shutdown_event = asyncio.Event()

try:
    loglevel = config['loglevel']
    log_file = config['log_file']
    tcp_port = config['tcp_port']
    ipset_goodguys = config['ipset_goodguys']
    ipset_badguys = config['ipset_badguys']
    ERROR_LOG_ENTRY = config['error_log_entry']
    sqllite_db = config['sqllite_db']
    geo_ip_country_db = config['geo_ip_country_db']
    # check if file exists:
    if len(str(geo_ip_country_db)) > 0 and not os.path.isfile(geo_ip_country_db):
        print(f"Error: GeoIP country database '{geo_ip_country_db}' does not exist. Exiting...")
        exit(1)
    geo_ip_city_db = config['geo_ip_city_db']
    # check if file exists:
    if len(str(geo_ip_city_db)) > 0 and not os.path.isfile(geo_ip_city_db):
        print(f"Error: GeoIP city database '{geo_ip_city_db}' does not exist. Exiting...")
        exit(1)
    knock_sequence = config['knock_sequence']
except KeyError as e:
    print(f"Error: Missing configuration key in config.json: {e}")
    exit(1)