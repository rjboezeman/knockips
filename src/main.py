#!/usr/bin/env python3
import asyncio
import os
import sys

from logReaders.localFile import LocalFile
from logConsumers.logFirewall import FirewallLogger
from logConsumers.manageIPset import IPSetManager
from logService.fastApiService import FastAPILogService
from config import log_file, shutdown_event, multi_queue, ERROR_LOG_ENTRY
from utils.logger import log

async def main():
    if not os.path.isfile(log_file):
        log.error(f"Error: The log file '{log_file}' does not exist. Exiting...")
        await multi_queue.put(ERROR_LOG_ENTRY)
        shutdown_event.set()
        return

    local_file = LocalFile(multi_queue, shutdown_event)
    shorewall_logger = FirewallLogger(multi_queue, shutdown_event)
    fast_api_service = FastAPILogService(multi_queue, shutdown_event)
    fast_api_service.set_log_processor(shorewall_logger)
    ipset_manager = IPSetManager(multi_queue, shutdown_event)
    ipset_manager.set_log_processor(shorewall_logger)

    tasks = [
        asyncio.create_task(local_file.run()),
        asyncio.create_task(shorewall_logger.run()),
        asyncio.create_task(fast_api_service.run()),
        asyncio.create_task(ipset_manager.run())
    ]
    
    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        log.error(f"An error occurred: {e}")
    finally:
        await shutdown(tasks)

async def shutdown(tasks):
    log.info("Shutting down...")
    for task in tasks:
        task.cancel()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            log.error(f"Task raised an exception: {result}")
    shutdown_event.set()

if __name__ == "__main__":
    if os.geteuid() != 0:
        log.error("Error: This script must be run as root. Please restart the script with 'sudo' or as the root user.")
        sys.exit(1)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.error("Received keyboard interrupt, shutting down...")
    except asyncio.exceptions.CancelledError:
        log.error("Received cancelled error, shutting down...")
    except Exception as e:
        log.error(f"An error occurred: {e}")
