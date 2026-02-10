"""
认证工具 - 密码验证和 Session 管理
"""
import uuid
from typing import Optional

# 简单的 session 存储(内存)
active_sessions = {}

def verify_password(password: str, expected_password: str) -> bool:
    """
    验证密码
    
    Args:
        password: 用户输入的密码
        expected_password: 期望的密码
    
    Returns:
        是否匹配
    """
    return password == expected_password

def create_session(user_id: int, role: str) -> str:
    """
    创建会话
    
    Args:
        user_id: 用户 ID
        role: 用户角色
    
    Returns:
        session_id
    """
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {
        'user_id': user_id,
        'role': role
    }
    return session_id

def get_session(session_id: str) -> Optional[dict]:
    """
    获取会话信息
    
    Args:
        session_id: 会话 ID
    
    Returns:
        会话信息字典或 None
    """
    return active_sessions.get(session_id)

def delete_session(session_id: str):
    """
    删除会话
    
    Args:
        session_id: 会话 ID
    """
    if session_id in active_sessions:
        del active_sessions[session_id]

def clear_all_sessions():
    """清空所有会话"""
    active_sessions.clear()
