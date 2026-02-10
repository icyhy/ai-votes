"""
网络工具 - IP 地址检测
"""
import socket

def get_local_ip() -> str:
    """
    自动检测本机局域网 IP 地址
    
    优先选择私有IP地址(10.x.x.x, 172.16-31.x.x, 192.168.x.x)
    排除回环地址和特殊网段
    
    Returns:
        IP 地址字符串,如 "192.168.1.100"
    """
    try:
        # 方法1: 尝试使用socket连接外部地址
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        
        # 验证获取的IP是否为有效的私有IP
        if _is_valid_private_ip(ip):
            return ip
            
        # 如果不是有效的私有IP，尝试方法2：遍历所有网卡
        return _get_best_local_ip()
        
    except Exception:
        # 如果方法1失败，尝试方法2
        try:
            return _get_best_local_ip()
        except Exception:
            # 所有方法都失败，返回 localhost
            return "127.0.0.1"

def _is_valid_private_ip(ip: str) -> bool:
    """
    检查IP是否为有效的私有IP地址
    
    Args:
        ip: IP地址字符串
        
    Returns:
        是否为有效的私有IP
    """
    if not ip or ip == "127.0.0.1":
        return False
    
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    
    try:
        first = int(parts[0])
        second = int(parts[1])
        
        # 10.0.0.0 - 10.255.255.255
        if first == 10:
            return True
        
        # 172.16.0.0 - 172.31.255.255
        if first == 172 and 16 <= second <= 31:
            return True
        
        # 192.168.0.0 - 192.168.255.255
        if first == 192 and second == 168:
            return True
        
        # 排除特殊网段 (如 198.18.x.x 是运营商级NAT)
        return False
        
    except ValueError:
        return False

def _get_best_local_ip() -> str:
    """
    遍历所有网卡，选择最合适的IP地址
    
    Returns:
        最合适的IP地址
    """
    import socket
    
    # 获取主机名
    hostname = socket.gethostname()
    # 获取所有IP地址
    ip_list = socket.gethostbyname_ex(hostname)[2]
    
    # 优先级：192.168.x.x > 10.x.x.x > 172.16-31.x.x
    best_ip = None
    for ip in ip_list:
        if not _is_valid_private_ip(ip):
            continue
        
        parts = ip.split('.')
        first = int(parts[0])
        
        # 最优先：192.168.x.x
        if first == 192:
            return ip
        
        # 次优先：10.x.x.x
        if first == 10:
            best_ip = ip
            continue
        
        # 最后：172.16-31.x.x
        if first == 172 and best_ip is None:
            best_ip = ip
    
    return best_ip if best_ip else "127.0.0.1"

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
