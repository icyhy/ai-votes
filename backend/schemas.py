"""
Pydantic 数据模型(用于 API 请求和响应)
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

# ===== 活动相关 =====
class ActivityCreate(BaseModel):
    name: str = Field(..., max_length=200)
    theme: Optional[str] = Field(None, max_length=500)

class ActivityResponse(BaseModel):
    id: int
    name: str
    theme: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ===== 投票相关 =====
class VoteCreate(BaseModel):
    activity_id: int
    title: str = Field(..., max_length=500)
    type: str = Field(..., pattern='^(single|multiple|text|rating)$')
    options: Optional[List[str]] = None  # 单选/多选的选项
    order_index: Optional[int] = None

class VoteUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    type: Optional[str] = Field(None, pattern='^(single|multiple|text|rating)$')
    options: Optional[List[str]] = None
    order_index: Optional[int] = None

class VoteResponse(BaseModel):
    id: int
    activity_id: int
    title: str
    type: str
    options: Optional[Any]
    order_index: Optional[int]
    
    class Config:
        from_attributes = True

# ===== 签到相关 =====
class SignInRequest(BaseModel):
    name: str = Field(..., max_length=100)
    department: Optional[str] = Field(None, max_length=200)
    role: str = Field(..., pattern='^(participant|host)$')
    password: Optional[str] = None  # 主持人需要密码

class SignInResponse(BaseModel):
    session_id: str
    redirect: str  # /participant 或 /host

# ===== 投票提交 =====
class VoteSubmit(BaseModel):
    vote_id: int
    answer: Any  # JSON 格式,根据投票类型不同

# ===== 密码更新 =====
class PasswordUpdate(BaseModel):
    admin_password: Optional[str] = None
    host_password: Optional[str] = None

# ===== 网络配置 =====
class NetworkConfig(BaseModel):
    manual_ip: str

# ===== 登录 =====
class LoginRequest(BaseModel):
    password: str

class LoginResponse(BaseModel):
    token: str
    message: str

# ===== 投票结果 =====
class VoteResult(BaseModel):
    option: str
    count: int
    percentage: str

class VoteResultResponse(BaseModel):
    vote_id: int
    results: List[VoteResult]

# ===== 活动统计 =====
class ActivitySummary(BaseModel):
    total_participants: int
    votes_completed: int
    votes_summary: List[dict]
