from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
app = FastAPI()

app.mount('/static',StaticFiles(directory='statics',html=True),name='static')

@app.get('/')
async def index():
    return FileResponse('templates/index.html')

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        print(data)
        await websocket.send_text(f"Message text was: {data}")