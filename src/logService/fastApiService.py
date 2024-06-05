from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from uvicorn import Config, Server
from pydantic import BaseModel
import asyncio
from config import multiQueue, shutdown_event
from logConsumers.logShorewall import parse_shorewall_log

class LogItem(BaseModel):
    log_lines: list[str]

app = FastAPI()

# Serve the static files from the 'static' directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        queue = multiQueue.signup()
        while True:
            log_line = await multiQueue.get(queue)
            await websocket.send_json(parse_shorewall_log(log_line))
    except WebSocketDisconnect:
        print("WebSocket disconnected")
        multiQueue.signout(queue)

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
