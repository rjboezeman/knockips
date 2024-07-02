from utils.knockIPBase import KnockIPBase
from utils.logger import log
import os
import asyncio
import aiofiles
import time
from config import log_file

class LocalFile(KnockIPBase):

    async def tail_log_file(self, log_file: str):
        if not os.path.isfile(log_file):
            log.error(f"Error: The log file '{log_file}' does not exist.")
            await self.do_shutdown()
            return

        try:
            current_inode = os.stat(log_file).st_ino
            async with aiofiles.open(log_file, mode='r') as f:
                await f.seek(0, 2)  # Move to the end of the file
                while not self.shutdown_event.is_set():
                    chunk = await f.read(1024)  # Read in small chunks
                    if chunk:
                        lines = chunk.splitlines(keepends=True)
                        for line in lines:
                            if line.endswith('\n'):
                                await self.put(line.strip())
                            else:
                                await asyncio.sleep(0.5)
                    else:
                        # Check if the file has been rotated
                        new_inode = os.stat(log_file).st_ino
                        if new_inode != current_inode:
                            log.warning(f"Log file '{log_file}' has been rotated. Reopening...")
                            current_inode = new_inode
                            break  # Break to reopen the file
                        await asyncio.sleep(0.5)
        except Exception as e:
            log.error(f"Error: {e}")
            await self.do_shutdown()


    async def process_log_line(self, log_line):
        log.debug('LocalFile process_log_line: ' + log_line)

    async def take_action(self, output):
        log.debug('LocalFile take_action: ' + output)

    async def run(self):
        self.signup()
        while not self.shutdown_event.is_set():
            await self.tail_log_file(log_file)
        self.signout()
    
    async def initialize(self):
        log.debug('LocalFile initialize')

    async def cleanup(self):
        pass
