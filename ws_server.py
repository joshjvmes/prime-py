import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from particle_field import ParticleField
from vispy import app as vispy_app

# Initialize the particle field (GPU off)
field = ParticleField(count=15000, size=10.0, use_gpu=False)

# Create FastAPI app and mount static files
app = FastAPI()
app.mount("/", StaticFiles(directory="reference/dist", html=True), name="static")

# Connected WebSocket clients
clients = set()

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    # Event listener to broadcast field events
    def on_event(msg):
        data = json.dumps(msg)
        asyncio.create_task(ws.send_text(data))
    field.add_listener(on_event)
    try:
        while True:
            text = await ws.receive_text()
            msg = json.loads(text)
            cmd = msg.get("command")
            args = msg.get("args", [])
            if hasattr(field, cmd):
                try:
                    getattr(field, cmd)(*args)
                except Exception as e:
                    await ws.send_text(json.dumps({"error": str(e)}))
            else:
                await ws.send_text(json.dumps({"error": f"Unknown command: {cmd}"}))
    except WebSocketDisconnect:
        pass
    finally:
        clients.discard(ws)
        field.remove_listener(on_event)

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)