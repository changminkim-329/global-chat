from fastapi import FastAPI,Depends,WebSocket, WebSocketDisconnect,HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from database.database import SessionLocal, ENGINE
from database.model import *
from database.schema import *
from pydantic import BaseModel
from typing import Dict,List, Optional,Union
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import timedelta
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import UploadFile,Form
from starlette.responses import RedirectResponse
import os
import re
from googletrans import Translator
from core.auth import *
from core.consts import *
from core.configs import *


translator = Translator()

app = FastAPI()
app.mount('/static',StaticFiles(directory='static'),name='static')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(ENGINE)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        pass

    finally:
        db.close()

@app.get('/login')
async def login():
    return FileResponse('templates/index.html')

@app.get('/signup')
async def signup():
    return FileResponse('templates/index.html')



# 예시 내 정보 불러오기
# 127.0.0.1:8080/api/v1/users?username=test
@app.get('/api/v1/users/{username}')
async def get_info(username:str, db=Depends(get_db)):
    # DB 조회, 수정, 업데이트, 삭제

    # 정보 조회
    try:
        user_info = db.query(User).filter(User.username == username).first()
        db.close()
        return user_info

    except Exception as e:
        print("에러")
        return "Not User"
    

@app.get('/join/success')
async def success_join():
    return FileResponse('templates/sign_up_success.html')

@app.get('/join/fail')
async def fail_join():
    return FileResponse('templates/sign_up_fail.html')
    
@app.post('/api/v1/join')
async def join(file: UploadFile, username: str = Form(), password: str = Form(),lang:str=Form(), db=Depends(get_db)):
    select_lang = 'ko' if lang == 'ko' else 'en'
    hashpw = pwd_context.hash(password)
    user = User(username=username,hashpw=hashpw,lang=select_lang,profile_pic='/static/pictures/'+username+'/profile.jpg')
   
    content = file.file.read()
    file.file.close()

    try:
        db.add(user)
        db.commit()

        path = './static/pictures/'+username
        if not os.path.isdir(path):
            os.mkdir(path)
        with open(path+'/profile.jpg',mode='wb') as f:
            f.write(content)
        return RedirectResponse(url='/join/success',status_code=302)

    except Exception as e:
        print(e)
        return RedirectResponse(url='/join/fail',status_code=302)



def verify_password(input_password, db_password):
    return pwd_context.verify(input_password, db_password)
    # return input_password == db_password

def get_userinfo(username: str,db): # username으로 조회할지, primary_key인 id로 조회할지...
    try:
        user_info:User = db.query(User).filter(User.username == username).first()
        return user_info
    
    except Exception as e:
        print('db에서 유저를 조회할 수 없습니다')
        print(e)
        return None

def authenticate_user(username: str, password: str, db):
    userinfo:Union[User,None] = get_userinfo(username,db)

    if not userinfo:
        return False

    db_password = userinfo.hashpw
    if not verify_password(password, db_password):
        return False
    return userinfo

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow()
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post('/api/v1/login', response_model=Token)
async def login_with_access_token(form_data: Login,db=Depends(get_db)):
    user:Union[User,None] = authenticate_user(username = form_data.username, password = form_data.password, db=db)
    if not user:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = 'Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'}
            )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub' : user.username, 'user_id' : user.id},
        expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'Bearer'}

def get_current_user(token: str = Depends(oauth2_scheme),db=Depends(get_db)):    
    credential_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail='인증되지 않았습니다',
        headers={'WWW-Authenticate': 'Bearer'}
    )


    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: Union[str,None] = payload.get('sub')
        if username is None:
            raise credential_exception
        
    except JWTError:
        raise credential_exception

    user_info = get_userinfo(username=username,db=db)
    if user_info is None:
        raise credential_exception
    return user_info

@app.get('/auth/me')
def read_users_me(current_active_user : User = Depends(get_current_user)):
    return current_active_user

#=============================================================#

@app.get('/api/v1/main-info/')
async def get_main_info(current_active_user : User = Depends(get_current_user),db=Depends(get_db)):
    # 정보 조회
    try:
        id = current_active_user.id
        user_lang = current_active_user.lang
        print("유저_언어:",user_lang)
        profile_path = {}

        me = db.query(
            User.username,User.profile_pic
        ).filter(
            (User.id == id)
        ).first()
        profile_path[me[0]] = me[1]
        username = me[0]

        messages = db.query(
            Friend.room_id,
            ).filter(
                (Friend.user_id == id),(Friend.state == 2)
            ).all()
        room_id_list = [ i[0] for i in set(messages)]

        rooms_info = {}
        for room_id in room_id_list:
            friend_ids = db.query(
                Friend.friend_id
            ).filter(
                Friend.room_id == room_id,
                Friend.user_id == id
            ).first()

            friends = db.query(
                User.username,User.profile_pic
            ).filter(
                User.id == friend_ids[0]
            ).first()

            profile_path[friends[0]] = friends[1]


            rooms_info['room-'+str(room_id)] = {
                "friend_name": friends[0],
                'room_id':room_id
            }
        
        rooms_messages = {}
        for room_id in room_id_list:
            rooms_messages['room-'+str(room_id)] = []
            messages = db.query(
                MessageHistory
                ).filter(
                    MessageHistory.room_id == room_id
                ).all()

            for message in messages:
                from_id = message.from_id
                created_at = message.created_at

                origin_lang = message.origin_message.lang
                if origin_lang == user_lang:
                    body = message.origin_message.body
                else:
                    body = message.result_message.body
                print(origin_lang,body)
                

                if from_id == id:
                    state = 'message me'
                else:
                    state = 'message'

                rooms_messages['room-'+str(room_id)].append({
                    'state':state,
                    'content':body,
                    'date':created_at
                })

        friend_list = db.query(
            Friend.friend_id
            ).filter(
                (Friend.user_id == id),(Friend.state == 1)
            ).all()

        friend_request_list = []
        for idx in friend_list:

            friends = db.query(
                User.username,User.profile_pic
            ).filter(
                (User.id == idx[0])
            ).first()
            friend_request_list.append(friends[0])
            profile_path[friends[0]]=friends[1]

        friend_list = db.query(
            Friend.friend_id
            ).filter(
                (Friend.user_id == id),(Friend.state == 0)
            ).all()

        friend_pend_list = []
        for idx in friend_list:

            friends = db.query(
                User.username,User.profile_pic
            ).filter(
                (User.id == idx[0])
            ).first()
            friend_pend_list.append(friends[0])
            profile_path[friends[0]]=friends[1]
        
        return {
            'username':username,
            'rooms_data':rooms_messages,'rooms_info':rooms_info,
            'friend_info':friend_request_list,
            'friend_pend_list':friend_pend_list,
            'profile_path':profile_path
            }

    except Exception as e:
        print("에러",e)
        return "Not User"

class Message(BaseModel):
    room_id:int
    content:str


@app.post('/api/v1/friend')
async def add_friends(friend_info:FriendCreate, current_active_user : User = Depends(get_current_user),db = Depends(get_db)):
    USER_ID = current_active_user.id;
    friend_exception = HTTPException(
        status_code = status.HTTP_400_BAD_REQUEST,
        detail='친구가 없습니다',
    )
    
    print(friend_info)
    try:
        friend_name = friend_info.friend_name
        friend = db.query(User).filter(User.username == friend_name).first()
        if friend:
            print(friend)
            friend_check = db.query(
                Friend
                ).filter(
                    (Friend.user_id == USER_ID),(Friend.friend_id == friend.id)
                ).first()

            if not friend_check:
                room_create = Room()
                db.add(room_create)
                db.commit()
                
                friend_create = Friend(
                    user_id=USER_ID,
                    friend_id=friend.id,
                    room_id=room_create.id
                    )
                db.add(friend_create)
                db.commit()

                friend_create = Friend(
                    user_id=friend.id,
                    friend_id=USER_ID,
                    room_id=room_create.id,
                    state=1
                    )

                db.add(friend_create)
                db.commit()
                return {'message':'success'}
            else:
                raise friend_exception

        else:
            raise friend_exception
                
    except Exception as e:
        print(e)
        raise friend_exception


@app.put('/api/v1/friend')
async def accept_friends(addfriend:AddFriend, current_active_user : User = Depends(get_current_user),db = Depends(get_db)):
    friend_name = addfriend.friend_name
    USER_ID = current_active_user.id;
    friend_data = db.query(User).filter(User.username == friend_name).first()
    FRIEND_ID = friend_data.id
    user = db.query(Friend).filter(
        (Friend.user_id == USER_ID),(Friend.friend_id == FRIEND_ID)).first()
    friend = db.query(Friend).filter(
        (Friend.user_id == FRIEND_ID),(Friend.friend_id == USER_ID)).first()

    print(user.state)
    print(friend.state)
    user.state = 2
    friend.state = 2
    db.commit()
    return {'hello':'world'}

class ConncectManager:
    def __init__(self):
        self.active_connections: Dict[int,WebSocket] = {}
        self.room_connections: Dict[str,List] = {}

    async def connect(self, client_id, websocket:WebSocket):
        await websocket.accept()
        if self.active_connections.get(client_id):
            self.disconnect(client_id)
            print(client_id," 삭제")
        self.active_connections[client_id] = websocket
        print("소켓 연결",self.active_connections)

    def disconnect(self, client_id):
        websocket = self.active_connections.pop(client_id)
        del websocket

    async def send_message(self, websocket_id:int, message:dict):
        await self.active_connections[websocket_id].send_json(message)

    async def broadcast(self, message: str):
        for idx, connection in self.active_connections.items():
            await connection.send_text(message)

manager = ConncectManager()

@app.websocket('/ws/chat')
async def websocket_endpoint(websocket: WebSocket, token:str, db=Depends(get_db)):
    try: 
        current_user = get_current_user(token,db)
        print("유저:",current_user.id," 입장")
        client_id= current_user.id
    except Exception as e:
        return {'error':'에러'}

    await manager.connect(client_id,websocket)
    while True:
        try:
            USER_ID = client_id
            data = await websocket.receive_json()
            content = data['content']
            room_id = data['room_id']
            print(content,room_id)
            message = Message(room_id=room_id, content=content)

            body = message.content
            room_id = message.room_id
            friend = db.query(
                Friend
            ).filter(
                Friend.user_id == client_id,
                Friend.is_deleted == False,
                Friend.room_id == room_id,
                Friend.state == 2,
            ).first()

            if friend:

                try:
                    friend_id = friend.friend_id
                    print("친구 아이디:",friend_id)
                    if re.compile(r'[a-zA-z]+').match(body):
                        lang = "en"
                    else:
                        lang = "ko"

                    
                    origin_create = OriginCreate(body=body,lang=lang)
                    origin_message = OriginMessage(**origin_create.dict())

                    db.add(origin_message)
                    db.commit()

                    if lang == "en":
                        result_body = translator.translate(body, src='en', dest='ko').text
                        result_lang = "ko"
                    else:
                        result_body = translator.translate(body, src='ko', dest='en').text
                        result_lang = "en"
                    result_create = ResultCreate(
                        body=result_body,
                        lang=result_lang
                    )
                    result_message = ResultMessage(
                        **result_create.dict(),
                        origin_id=origin_message.id
                    )
                    db.add(result_message)
                    db.commit()

                    message_history = MessageHistory(
                        room_id=room_id,
                        from_id=USER_ID,
                        to_id=friend_id,
                        origin_id=origin_message.id,
                        result_id=result_message.id
                    )
                    

                    db.add(message_history)
                    db.commit()

                    if friend.friends.lang == lang:
                        send_body = origin_message.body
                    else:
                        send_body = result_message.body
                    print("보낼 메시지",send_body,friend.friends.lang,friend.friend_id)
                    message = {
                        'room_id':'room-'+str(room_id),
                        'state':'message',
                        'content':send_body,
                        'date':str(message_history.created_at)
                    }

                    # await websocket.send_json(message)
                    await manager.send_message(friend_id,message)
                except Exception as e:
                    print(e)


        except WebSocketDisconnect:
            manager.disconnect(client_id)


@app.get("/ai/test")
async def get_ai(message:str):
    if re.compile(r'[a-zA-z]+').match(message):
        data = translator.translate(message, src='en', dest='ko').text

    else:
        data = translator.translate(message, src='ko', dest='en').text
    return {'message':data}