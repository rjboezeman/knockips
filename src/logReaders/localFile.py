from config import multiQueue, shutdown_event, ERROR_LOG_ENTRY
import os
import asyncio
import aiofiles

queue = multiQueue.signup()

async def tail_logfile(logfile: str):
    if not os.path.isfile(logfile):
        print(f"Error: The log file '{logfile}' does not exist.")
        await multiQueue.put(ERROR_LOG_ENTRY)
        shutdown_event.set()
        return

    try:
        async with aiofiles.open(logfile, mode='r') as f:
            # Go to the end of the file
            await f.seek(0, 2)
            while not shutdown_event.is_set():
                line = await f.readline()
                if not line:
                    await asyncio.sleep(0.1)
                    continue
                await multiQueue.put(line.strip())
    except Exception as e:
        print(f"Error: {e}")
        await multiQueue.put(ERROR_LOG_ENTRY)
        shutdown_event.set()