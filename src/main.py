#!/usr/bin/env python3
import asyncio
import os
import sys
import signal

from logReaders.localFile import LocalFile
from logConsumers.logFirewall import FirewallLogger
from logConsumers.manageIPset import IPSetManager
from logConsumers.storeDataSQLLite import SQLLiteDataStore
from logService.fastApiService import FastAPILogService
from config import log_file, shutdown_event, log_multi_queue, actor_multi_queue, ERROR_LOG_ENTRY
from utils.logger import log

async def main():
    if not os.path.isfile(log_file):
        log.error(f"Error: The log file '{log_file}' does not exist. Exiting...")
        await log_multi_queue.put(ERROR_LOG_ENTRY)
        shutdown_event.set()
        return

    local_file = LocalFile(log_multi_queue, shutdown_event)
    firewall_logger = FirewallLogger(log_multi_queue, shutdown_event)
    fast_api_service = FastAPILogService(log_multi_queue, shutdown_event)
    fast_api_service.set_log_processor(firewall_logger)
    ipset_manager = IPSetManager(log_multi_queue, shutdown_event)
    ipset_manager.set_log_processor(firewall_logger)
    store_sql_data = SQLLiteDataStore(log_multi_queue, shutdown_event)
    store_sql_data.set_log_processor(firewall_logger)

    tasks = [
        asyncio.create_task(local_file.run()),
        asyncio.create_task(firewall_logger.run()),
        asyncio.create_task(fast_api_service.run()),
        asyncio.create_task(ipset_manager.run()),
        asyncio.create_task(store_sql_data.run())
    ]
    
    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        log.error(f"An error occurred: {e}")
    finally:
        for task in tasks:
            task.cancel()
        # Await tasks to ensure they are properly cancelled
        await asyncio.gather(*tasks, return_exceptions=True)

def handle_signal(signum, frame):
    log.info(f"Received signal {signum}, shutting down...")
    shutdown_event.set()

if __name__ == "__main__":
    if os.geteuid() != 0:
        log.error("Error: This script must be run as root. Please restart the script with 'sudo' or as the root user.")
        sys.exit(1)

    # Register signal handlers
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)  # Handle SIGINT (Ctrl+C) as well
    signal.signal(signal.SIGHUP, handle_signal)  # Handle SIGHUP (sent by systemd when service is stopped/restarted)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.error("Received keyboard interrupt, shutting down...")
    except asyncio.exceptions.CancelledError:
        log.error("Received cancelled error, shutting down...")
    except Exception as e:
        log.error(f"An error occurred: {e}")
    finally:
        log.info("Shutting down...")
        shutdown_event.set()
