#!/usr/bin/env python3
import asyncio
import os
import sys

from logReaders.localFile import LocalFile
from logConsumers.logShorewall import ShorewallLogger
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
    shorewall_logger = ShorewallLogger(multi_queue, shutdown_event)
    fast_api_service = FastAPILogService(multi_queue, shutdown_event)
    fast_api_service.set_log_processor(shorewall_logger)
    
    await asyncio.gather(
        local_file.run(),
        shorewall_logger.run(),
        fast_api_service.run()
    )

if __name__ == "__main__":
    if os.geteuid() != 0:
        log.error("Error: This script must be run as root. Please restart the script with 'sudo' or as the root user.")
        sys.exit(1)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.error("Received keyboard interrupt, shutting down...")
        shutdown_event.set()
