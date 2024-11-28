from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from web_socket import ConnectionManager
from uuid import uuid4
import json

app = FastAPI()
# Specify the directory for templates
templates = Jinja2Templates(directory="templates")

manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("client.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(uuid4())
    try:
        await manager.connect(websocket, client_id)
        while True:
            data = await websocket.receive_text()
            _data = json.loads(data)
            message_type = _data.get("type")
            if message_type == "broadcast":
                await manager.broadcast(_data.get("message"), _data.get("sender"))
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        await manager.disconnect(client_id)
