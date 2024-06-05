# FastAPI setup
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from uvicorn import Config, Server
from pydantic import BaseModel
import asyncio
from config import log_queue, shutdown_event

class LogItem(BaseModel):
    log_lines: list[str]

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Log file tailing service"}

@app.get("/logs", response_model=LogItem)
async def get_logs():
    logs = []
    while not log_queue.empty():
        logs.append(await log_queue.get())
    return JSONResponse(content={"log_lines": logs})



async def start_uvicorn():
    config = Config(app, host="0.0.0.0", port=8000, loop="asyncio")
    server = Server(config)

    # Run the server in a background task
    server_task = asyncio.create_task(server.serve())

    try:
        while not shutdown_event.is_set():
            await asyncio.sleep(1)
    finally:
        server.should_exit = True
        await server_task