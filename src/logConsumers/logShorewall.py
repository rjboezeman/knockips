from config import log_queue, shutdown_event, ERROR_LOG_ENTRY
import re

async def log_consumer():
    while not shutdown_event.is_set() or not log_queue.empty():
        log_line = await log_queue.get()
        if log_line == ERROR_LOG_ENTRY:
            print("Received error signal, shutting down log consumer.")
            shutdown_event.set()
            break
        logdict = parse_shorewall_log(log_line)
        if logdict:
            print(logdict)
        else:
            print(f"Failed to parse log line: {log_line}")
        # You can add more processing logic here

def parse_shorewall_log(log_line):
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
        return match.groupdict()
    else:
        return None