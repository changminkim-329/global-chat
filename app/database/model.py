from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Integer, String, ForeignKey,Boolean, DateTime,Column
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer,primary_key=True,index=True)
    username = Column(String(20),unique=True)
    hashpw = Column(String(40))
    profile_pic = Column(String(100))
    is_active = Column(Boolean,default=True)
    lang = Column(String(10))
    friend_count = Column(Integer,default=0)
    created_at = Column(DateTime,default=datetime.utcnow)
    updated_at = Column(DateTime,default=datetime.utcnow)

    
class Friend(Base):
    __tablename__ = 'friends'
    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,ForeignKey('user.id'))
    friend_id = Column(Integer,ForeignKey('user.id'))
    is_deleted = Column(Boolean,default=False) # 친구 삭제
    state = Column(Integer,default=0) # 요청대기: 0, 요청미응답: 1, 요청완료: 2
    room_id = Column(Integer,ForeignKey('room.id'))
    users = relationship("User",foreign_keys=[user_id])
    friends = relationship("User",foreign_keys=[friend_id])
    rooms = relationship("Room",foreign_keys=[room_id])
    

class Room(Base):
    __tablename__ = 'room'
    id = Column(Integer,primary_key=True,index=True)
    created_at = Column(DateTime,default=datetime.utcnow)
    
    friends = relationship("Friend")
    # message_historys = relationship("MessageHistory")

class MessageHistory(Base):
    __tablename__ = 'message_history'
    id = Column(Integer,primary_key=True,index=True)
    room_id = Column(Integer,ForeignKey('room.id'))
    rooms = relationship("Room",foreign_keys=[room_id])

    from_id = Column(Integer)
    to_id = Column(Integer)

    origin_id = Column(Integer,ForeignKey('origin_message.id'))
    origin_message = relationship("OriginMessage",foreign_keys=[origin_id],back_populates="message_history")

    result_id = Column(Integer,ForeignKey('result_message.id'))
    result_message = relationship("ResultMessage",foreign_keys=[result_id],back_populates="message_history")

    created_at = Column(DateTime,default=datetime.utcnow)

class OriginMessage(Base):
    __tablename__ = 'origin_message'
    id = Column(Integer,primary_key=True,index=True)
    message_history = relationship("MessageHistory",back_populates="origin_message",uselist=False)
    body = Column(String(100))
    lang = Column(String(10))

    

class ResultMessage(Base):
    __tablename__ = 'result_message'
    id = Column(Integer,primary_key=True,index=True)
    message_history = relationship("MessageHistory",back_populates="result_message",uselist=False)

    origin_id = Column(Integer,ForeignKey('origin_message.id'))
    body = Column(String(100))
    lang = Column(String(10))


    


