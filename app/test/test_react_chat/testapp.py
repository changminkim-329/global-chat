from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import WebSocket

app = FastAPI()

origins =[
    'http://127.0.0.1:3000',
    'http://localhost:3000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class User(BaseModel):
    firstname:str
    age:int

# axios 테스트
@app.post('/api/user')
async def get_user(user:User):
    print(user)

    return {
        'room_id':'room-1',
        'state':'message',
        'content':'안녕하세요.',
        'date':"2022.12.01 09:46 AM"
    }

@app.get('/api/main-info/{id}')
async def get_main_info(id:int):
    id = 1

    room_1_data = [
        {
            "state":"message",
            "content":"We've got some killer ideas kicking about already.",
            "date":"2022.12.01 09:46 AM"
        },
        {
            "state":"message me",
            "content":"Can't wait! How are we coming along with the client?",
            "date":"2022.12.01 09:46 AM"
        },
        {
            "state":"message",
            "content":"어이 드래곤 창~ 덤벼라.",
            "date":"2022.12.01 09:46 AM"
        },
        {
            "state":"message",
            "content":"동작 그만 밑장 뺴기? 뭐야 내가 빙다리 핫바지로 보이냐 증거 있어? 넌 나한테 9땡을 주었을 것이고 이거이거 장자리 아니여",
            "date":"2022.12.01 09:46 AM"
        },
    ]

    room_2_data = [
        {
            "state":"message",
            "content":"We've got some killer ideas kicking about already.",
            "date":"2022.12.01 09:46 AM"
        },
        {
            "state":"message me",
            "content":"Can't wait! How are we coming along with the client?",
            "date":"2022.12.01 09:46 AM"
        },
        {
            "state":"message",
            "content":"어이 드래곤 창~ 덤벼라.",
            "date":"2022.12.01 09:46 AM"
        },
        {
            "state":"message",
            "content":"동작 그만 밑장 뺴기? 뭐야 내가 빙다리 핫바지로 보이냐 증거 있어? 넌 나한테 9땡을 주었을 것이고 이거이거 장자리 아니여",
            "date":"2022.12.01 09:46 AM"
        },
    ]

    print("데이터 송출");
    
    rooms_data = {
        'room-1':room_1_data,
        'room-2':room_2_data
    }

    return {'rooms_data':rooms_data}


@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        print(data)
        await websocket.send_json({
        'room_id':'room-1',
        'state':'message',
        'content':'안녕하세요.',
        'date':"2022.12.01 09:46 AM"
        })
