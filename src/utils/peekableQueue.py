import asyncio

class PeekableQueue:
    def __init__(self):
        self._queue = asyncio.Queue()
        self._peek_buffer = None

    async def put(self, item):
        await self._queue.put(item)

    async def get(self):
        if self._peek_buffer is not None:
            item = self._peek_buffer
            self._peek_buffer = None
            return item
        return await self._queue.get()

    async def peek(self):
        if self._peek_buffer is None:
            self._peek_buffer = await self._queue.get()
        return self._peek_buffer

    def empty(self):
        return self._queue.empty() and self._peek_buffer is None

    def qsize(self):
        size = self._queue.qsize()
        if self._peek_buffer is not None:
            size += 1
        return size