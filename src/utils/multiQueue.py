import asyncio
import copy

class MultiQueue:
    def __init__(self):
        self.queues = []

    async def put(self, item):
        for queue in self.queues:
            await queue.put(copy.deepcopy(item))

    def signup(self):
        queue = asyncio.Queue()
        self.queues.append(queue)
        return queue

    def signout(self, queue):
        if queue in self.queues:
            self.queues.remove(queue)
            # Clear the queue when signing out
            while not queue.empty():
                queue.get_nowait()
        else:
            raise ValueError("Queue not found")

    async def get(self, queue):
        if queue in self.queues:
            return await queue.get()
        else:
            raise ValueError("Queue not found")

    def qsize(self, queue):
        if queue in self.queues:
            return queue.qsize()
        else:
            raise ValueError("Queue not found")

    def empty(self, queue):
        if queue in self.queues:
            return queue.empty()
        else:
            raise ValueError("Queue not found")