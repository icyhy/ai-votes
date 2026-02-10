"""
数据库迁移脚本 - 添加 vote_templates 表
"""
from backend.database import engine, init_db
from backend.models import Base
from sqlalchemy import text

print("正在更新数据库架构...")

# 检查是否需要创建 vote_templates 表
with engine.connect() as conn:
    # 检查 vote_templates 表是否已存在
    result = conn.execute(text(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='vote_templates'"
    ))
    table_exists = result.fetchone() is not None
    
    if table_exists:
        print("✓ vote_templates 表已存在，无需迁移")
    else:
        print("→ vote_templates 表不存在，正在创建...")
        # 创建新表
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("✓ vote_templates 表创建成功")

print("\n数据库迁移完成！")
