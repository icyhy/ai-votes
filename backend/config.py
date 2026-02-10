"""
配置管理模块
"""
import json
import os
from pathlib import Path
from typing import Optional

class Settings:
    """系统配置类"""
    
    def __init__(self):
        self.config_path = Path("config/settings.json")
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.admin_password = config.get('admin_password', 'admin123')
                self.host_password = config.get('host_password', 'host123')
                self.manual_ip = config.get('manual_ip', '')
                self.port = config.get('port', 8000)
                self.database_url = config.get('database_url', 'sqlite:///./data/database.db')
        else:
            # 默认配置
            self.admin_password = 'admin123'
            self.host_password = 'host123'
            self.manual_ip = ''
            self.port = 8000
            self.database_url = 'sqlite:///./data/database.db'
    
    def save_config(self):
        """保存配置到文件"""
        config = {
            'admin_password': self.admin_password,
            'host_password': self.host_password,
            'manual_ip': self.manual_ip,
            'port': self.port,
            'database_url': self.database_url
        }
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def update_passwords(self, admin_password: Optional[str] = None, host_password: Optional[str] = None):
        """更新密码"""
        if admin_password:
            self.admin_password = admin_password
        if host_password:
            self.host_password = host_password
        self.save_config()
    
    def update_network(self, manual_ip: str):
        """更新网络配置"""
        self.manual_ip = manual_ip
        self.save_config()

# 全局配置实例
settings = Settings()
