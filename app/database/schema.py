import enum 
from datetime import datetime
from pydantic import BaseModel

# class LangEnum(enum.Enum):
#     ko = "ko" # 한글
#     en = "en" # 영어 

class UserCreate(BaseModel):
    username: str
    hashpw: str
    profile_pic: str
    lang:str

class FriendCreate(BaseModel):
    friend_name: str
    
class OriginCreate(BaseModel):
    body:str
    lang:str

class ResultCreate(BaseModel):
    body:str
    lang:str

class MessageCreate(BaseModel):
    room_id:int
    from_id:int
    to_id:int

class Token(BaseModel):
    access_token: str
    token_type: str

class Login(BaseModel):
    username:str
    password:str

class AddFriend(BaseModel):
    friend_name:str