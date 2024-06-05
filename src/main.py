#!/usr/bin/env python3
import asyncio
import os

from logConsumers.logShorewall import log_consumer
from logReaders.localFile import tail_logfile
from logService.fastApiService import start_uvicorn
from config import logfile, shutdown_event

async def main():
    if not os.path.isfile(logfile):
        print(f"Error: The log file '{logfile}' does not exist. Exiting...")
        await log_queue.put(ERROR_LOG_ENTRY)
        shutdown_event.set()
        return

    await asyncio.gather(
        tail_logfile(logfile),
        log_consumer(),
        start_uvicorn()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Received keyboard interrupt, shutting down...")
        shutdown_event.set()
