"""
管理员 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import (
    ActivityCreate, ActivityResponse,
    VoteCreate, VoteUpdate, VoteResponse,
    VoteTemplateCreate, VoteTemplateUpdate, VoteTemplateResponse,
    PasswordUpdate, NetworkConfig,
    LoginRequest, LoginResponse
)
from backend.services import ActivityService, VoteService, VoteTemplateService, ExportService
from backend.config import settings
from backend.utils import verify_password
from typing import List
import json
from pathlib import Path

router = APIRouter(prefix="/api/admin", tags=["admin"])

# 简单的认证令牌(实际项目中应使用 JWT)
admin_tokens = set()

@router.post("/login", response_model=LoginResponse)
async def admin_login(request: LoginRequest):
    """管理员登录"""
    if verify_password(request.password, settings.admin_password):
        token = f"admin_{len(admin_tokens)}"
        admin_tokens.add(token)
        return LoginResponse(token=token, message="登录成功")
    raise HTTPException(status_code=401, detail="密码错误")

def verify_admin_token(token: str = Query(..., description="管理员令牌")):
    """验证管理员令牌"""
    if token not in admin_tokens:
        raise HTTPException(status_code=401, detail="令牌无效或已过期,请重新登录")
    return token

@router.post("/activities", response_model=ActivityResponse)
async def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db),
    token: str = Depends(verify_admin_token)
):
    """创建活动"""
    db_activity = ActivityService.create_activity(db, activity)
    return db_activity

@router.get("/activities/current", response_model=ActivityResponse)
async def get_current_activity(
    db: Session = Depends(get_db),
    token: str = Depends(verify_admin_token)
):
    """获取当前活动"""
    activity = ActivityService.get_current_activity(db)
    if not activity:
        raise HTTPException(status_code=404, detail="没有活动")
    return activity

@router.post("/votes", response_model=VoteResponse)
async def create_vote(
    vote: VoteCreate,
    db: Session = Depends(get_db),
    token: str = Depends(verify_admin_token)
):
    """创建投票"""
    db_vote = VoteService.create_vote(db, vote)
    # 解析 options JSON
    if db_vote.options:
        db_vote.options = json.loads(db_vote.options)
    return db_vote

@router.get("/votes/{activity_id}", response_model=List[VoteResponse])
async def get_votes(
    activity_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(verify_admin_token)
):
    """获取活动的所有投票"""
    votes = VoteService.get_votes_by_activity(db, activity_id)
    # 解析 options JSON
    for vote in votes:
        if vote.options:
            vote.options = json.loads(vote.options)
    return votes

@router.put("/votes/{vote_id}", response_model=VoteResponse)
async def update_vote(
    vote_id: int,
    vote_update: VoteUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(verify_admin_token)
):
    """更新投票"""
    db_vote = VoteService.update_vote(db, vote_id, vote_update)
    if not db_vote:
        raise HTTPException(status_code=404, detail="投票不存在")
    if db_vote.options:
        db_vote.options = json.loads(db_vote.options)
    return db_vote

@router.delete("/votes/{vote_id}")
async def delete_vote(
    vote_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(verify_admin_token)
):
    """删除投票"""
    success = VoteService.delete_vote(db, vote_id)
    if not success:
        raise HTTPException(status_code=404, detail="投票不存在")
    return {"message": "删除成功"}

@router.post("/passwords")
async def update_passwords(
    passwords: PasswordUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(verify_admin_token)
):
    """更新密码"""
    settings.update_passwords(passwords.admin_password, passwords.host_password)
    return {"message": "密码更新成功"}

@router.post("/network")
async def update_network(
    config: NetworkConfig,
    db: Session = Depends(get_db),
    token: str = Depends(verify_admin_token)
):
    """更新网络配置"""
    settings.update_network(config.manual_ip)
    return {"message": "网络配置更新成功"}

@router.get("/exports")
async def list_exports(token: str = Depends(verify_admin_token)):
    """列出所有导出文件"""
    files = ExportService.list_export_files()
    return {"files": files}

@router.get("/exports/{filename}")
async def download_export(
    filename: str,
    token: str = Depends(verify_admin_token)
):
    """下载导出文件"""
    filepath = Path("data/exports") / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(filepath, filename=filename)

@router.delete("/exports/{filename}")
async def delete_export(
    filename: str,
    token: str = Depends(verify_admin_token)
):
    """删除导出文件"""
    success = ExportService.delete_export_file(filename)
    if not success:
        raise HTTPException(status_code=404, detail="文件不存在或删除失败")
    return {"message": "删除成功"}

# ===== 投票模板管理 =====

@router.post("/vote-templates", response_model=VoteTemplateResponse)
async def create_vote_template(
    template: VoteTemplateCreate,
    db: Session = Depends(get_db),
    token: str = Depends(verify_admin_token)
):
    """创建投票模板"""
    db_template = VoteTemplateService.create_template(
        db, template.title, template.type, template.options, template.order_index
    )
    # 解析 options JSON
    if db_template.options:
        db_template.options = json.loads(db_template.options)
    return db_template

@router.get("/vote-templates", response_model=List[VoteTemplateResponse])
async def get_vote_templates(
    db: Session = Depends(get_db),
    token: str = Depends(verify_admin_token)
):
    """获取所有投票模板"""
    templates = VoteTemplateService.get_all_templates(db)
    # 解析 options JSON
    for template in templates:
        if template.options:
            template.options = json.loads(template.options)
    return templates

@router.put("/vote-templates/{template_id}", response_model=VoteTemplateResponse)
async def update_vote_template(
    template_id: int,
    template_update: VoteTemplateUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(verify_admin_token)
):
    """更新投票模板"""
    db_template = VoteTemplateService.update_template(
        db, template_id, template_update.title, template_update.type,
        template_update.options, template_update.order_index
    )
    if not db_template:
        raise HTTPException(status_code=404, detail="投票模板不存在")
    if db_template.options:
        db_template.options = json.loads(db_template.options)
    return db_template

@router.delete("/vote-templates/{template_id}")
async def delete_vote_template(
    template_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(verify_admin_token)
):
    """删除投票模板"""
    success = VoteTemplateService.delete_template(db, template_id)
    if not success:
        raise HTTPException(status_code=404, detail="投票模板不存在")
    return {"message": "删除成功"}
