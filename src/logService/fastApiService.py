from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from uvicorn import Config, Server
from pydantic import BaseModel
from utils.knockIPBase import KnockIPBase
import logging
from utils.logger import log, loglevel, handler
from config import tcp_port, current_script_dir
import asyncio

class LogItem(BaseModel):
    log_lines: list[str]

class FastAPILogService(KnockIPBase):

    def __init__(self, multi_queue, shutdown_event):
        super().__init__(multi_queue, shutdown_event)
        self.app = FastAPI()
        self.app.logger = log
        self.app.mount(f"/static", StaticFiles(directory=f"{current_script_dir}/static"), name="static")
        
        @self.app.get("/")
        async def read_root():
            return FileResponse('static/index.html')

        @self.app.websocket("/ws/logs")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.signup()
            send_task = asyncio.create_task(self.send_logs(websocket))
            receive_task = asyncio.create_task(self.receive_logs(websocket))
            try:
                await asyncio.gather(send_task, receive_task)
            except WebSocketDisconnect:
                log.warning("WebSocket disconnected")
                self.signout()
            finally:
                send_task.cancel()
                receive_task.cancel()
                self.signout()

        # Adding the routes after defining them
        self.app.add_api_route("/", read_root)
        self.app.add_api_websocket_route("/ws/logs", websocket_endpoint)

    async def send_logs(self, websocket: WebSocket):
        while True:
            log_line = await self.get()
            dict_item = await self.log_processor.process_log_line(log_line)
            await websocket.send_json(dict_item)

    async def receive_logs(self, websocket: WebSocket):
        while True:
            data = await websocket.receive_json()
            await self.process_received_data(data)

    async def process_received_data(self, data):
        # Process the received data here
        # log.info(f"Received data: {data}")
        pass

    async def start_uvicorn(self):
        config = Config(self.app, host="0.0.0.0", port=tcp_port, loop="asyncio")
        server = Server(config)
        uvicorn_logger = ['uvicorn', 'uvicorn.error', 'uvicorn.access', 'uvicorn.asgi']
        for logger_name in uvicorn_logger:
            logger = logging.getLogger(logger_name)
            logger.setLevel(loglevel)
            logger.addHandler(handler)
            logger.propagate = False
        
        # Run the server in a background task
        try:
            server_task = asyncio.create_task(server.serve())
            while not self.is_shutting_down():
                await asyncio.sleep(1)
        except asyncio.exceptions.CancelledError:
            log.error("Received cancelled error, shutting down...")
        finally:
            server.should_exit = True
            await server_task

    async def process_log_line(self, log_line):
        log.debug('FastAPILogService process_log_line: ' + log_line)

    async def take_action(self, output):
        log.debug('FastAPILogService take_action: ' + output)

    async def run(self):
        await self.start_uvicorn()