from utils.knockIPBase import KnockIPBase
from utils.logger import log
import os
import asyncio
import aiofiles
from config import log_file


class LocalFile(KnockIPBase):

    async def tail_log_file(self, log_file: str):
        if not os.path.isfile(log_file):
            log.error(f"Error: The log file '{log_file}' does not exist.")
            await self.do_shutdown()
            return

        try:
            async with aiofiles.open(log_file, mode='r') as f:
                # Go to the end of the file:
                await f.seek(0, 2)
                while not self.shutdown_event.is_set():
                    line = await f.readline()
                    if not line:
                        await asyncio.sleep(0.5)
                        continue
                    await self.put(line.strip())
        except Exception as e:
            log.error(f"Error: {e}")
            await self.do_shutdown()

    async def process_log_line(log_line):
        log.debug('LocalFile process_log_line: ' + log_line)

    async def take_action(self, output):
        log.debug('LocalFile take_action: ' + output)

    async def run(self):
        self.signup()
        await self.tail_log_file(log_file)
        self.signout()
        