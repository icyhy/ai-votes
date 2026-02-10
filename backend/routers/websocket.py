"""
WebSocket 连接管理器
"""
from fastapi import WebSocket
from typing import List, Dict
import json

class ConnectionManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        # 存储所有活跃的 WebSocket 连接
        self.active_connections: List[WebSocket] = []
        # 按类型分组的连接
        self.connections_by_type: Dict[str, List[WebSocket]] = {
            'display': [],      # 大屏
            'host': [],         # 主持人
            'participant': []   # 参会人
        }
        # 缓存当前状态以便新连接同步
        self.current_vote_id = None
        self.current_status = 'pending' # pending, active, voting, result, summary
    
    async def connect(self, websocket: WebSocket, client_type: str = 'display'):
        """
        接受新的 WebSocket 连接
        
        Args:
            websocket: WebSocket 连接对象
            client_type: 客户端类型 (display/host/participant)
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        if client_type in self.connections_by_type:
            self.connections_by_type[client_type].append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """
        断开 WebSocket 连接
        
        Args:
            websocket: WebSocket 连接对象
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # 从分组中移除
        for connections in self.connections_by_type.values():
            if websocket in connections:
                connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """
        广播消息到所有连接
        
        Args:
            message: 消息字典
        """
        # 移除已断开的连接
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)
        
        # 清理断开的连接
        for connection in dead_connections:
            self.disconnect(connection)
    
    async def send_to_type(self, client_type: str, message: dict):
        """
        发送消息到特定类型的客户端
        
        Args:
            client_type: 客户端类型
            message: 消息字典
        """
        if client_type not in self.connections_by_type:
            return
        
        dead_connections = []
        for connection in self.connections_by_type[client_type]:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)
        
        # 清理断开的连接
        for connection in dead_connections:
            self.disconnect(connection)
    
    async def send_to_display(self, message: dict):
        """发送消息到大屏"""
        await self.send_to_type('display', message)
    
    async def send_to_host(self, message: dict):
        """发送消息到主持人"""
        await self.send_to_type('host', message)
    
    async def send_to_participants(self, message: dict):
        """发送消息到所有参会人"""
        await self.send_to_type('participant', message)

# 全局 WebSocket 管理器实例
manager = ConnectionManager()
