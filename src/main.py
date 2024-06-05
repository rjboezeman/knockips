#!/usr/bin/env python3
import asyncio
import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import aiofiles
from uvicorn import Config, Server

# Reading configuration
with open('config.json') as config_file:
    config = json.load(config_file)

logfile = config['logfile']

# FastAPI setup
app = FastAPI()
log_queue = asyncio.Queue()

class LogItem(BaseModel):
    log_lines: List[str]

@app.get("/")
async def read_root():
    return {"message": "Log file tailing service"}

@app.get("/logs", response_model=LogItem)
async def get_logs():
    logs = []
    while not log_queue.empty():
        logs.append(await log_queue.get())
    return JSONResponse(content={"log_lines": logs})

async def tail_logfile(logfile: str):
    if not os.path.isfile(logfile):
        print(f"Error: The log file '{logfile}' does not exist.")
        return

    async with aiofiles.open(logfile, mode='r') as f:
        # Go to the end of the file
        await f.seek(0, 2)
        while True:
            line = await f.readline()
            if not line:
                await asyncio.sleep(0.1)
                continue
            await log_queue.put(line.strip())

async def log_consumer():
    while True:
        log_line = await log_queue.get()
        print(f"Processed log line: {log_line}")
        # You can add more processing logic here

async def start_uvicorn():
    config = Config(app, host="0.0.0.0", port=8000, loop="asyncio")
    server = Server(config)
    await server.serve()

async def main():
    if not os.path.isfile(logfile):
        print(f"Error: The log file '{logfile}' does not exist. Exiting...")
        return

    await asyncio.gather(
        tail_logfile(logfile),
        log_consumer(),
        start_uvicorn()
    )

if __name__ == "__main__":
    asyncio.run(main())
