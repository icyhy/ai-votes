"""
网络工具 - IP 地址检测
"""
import socket

def get_local_ip() -> str:
    """
    自动检测本机局域网 IP 地址
    
    Returns:
        IP 地址字符串,如 "192.168.1.100"
    """
    try:
        # 创建一个 UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接到外部地址(不会真正发送数据)
        s.connect(('8.8.8.8', 80))
        # 获取本地 IP
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # 如果失败,返回 localhost
        return "127.0.0.1"

def get_server_url(manual_ip: str = "", port: int = 8000) -> str:
    """
    获取服务器访问 URL
    
    Args:
        manual_ip: 手动配置的 IP 地址
        port: 端口号
    
    Returns:
        完整的服务器 URL
    """
    if manual_ip:
        ip = manual_ip
    else:
        ip = get_local_ip()
    
    return f"http://{ip}:{port}"
