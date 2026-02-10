"""
二维码生成工具
"""
import qrcode
from io import BytesIO
import base64

def generate_qrcode(url: str, size: int = 300) -> str:
    """
    生成二维码并返回 base64 编码的图片
    
    Args:
        url: 二维码内容(URL)
        size: 二维码大小(像素)
    
    Returns:
        base64 编码的 PNG 图片字符串
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 调整大小
    img = img.resize((size, size))
    
    # 转换为 base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"
