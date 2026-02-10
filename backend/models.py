"""
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Activity(Base):
    """活动表"""
    __tablename__ = 'activities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    theme = Column(String(500))
    status = Column(String(20), default='pending')  # pending, active, ended
    created_at = Column(DateTime, server_default=func.now())

class Vote(Base):
    """投票表"""
    __tablename__ = 'votes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey('activities.id'), nullable=False)
    title = Column(String(500), nullable=False)
    type = Column(String(20), nullable=False)  # single, multiple, text, rating
    options = Column(Text)  # JSON 格式
    order_index = Column(Integer)

class Participant(Base):
    """参会人表"""
    __tablename__ = 'participants'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey('activities.id'), nullable=False)
    name = Column(String(100), nullable=False)
    department = Column(String(200))
    role = Column(String(20), default='participant')  # participant, host
    session_id = Column(String(100), unique=True)
    signed_in_at = Column(DateTime, server_default=func.now())

class VoteRecord(Base):
    """投票记录表"""
    __tablename__ = 'vote_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vote_id = Column(Integer, ForeignKey('votes.id'), nullable=False)
    participant_id = Column(Integer, ForeignKey('participants.id'), nullable=False)
    answer = Column(Text, nullable=False)  # JSON 格式
    voted_at = Column(DateTime, server_default=func.now())
