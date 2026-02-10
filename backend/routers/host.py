"""
主持人 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services import ActivityService, VoteService, ParticipantService, ExportService
from backend.routers.websocket import manager
from typing import Optional
import json

router = APIRouter(prefix="/api/host", tags=["host"])

def get_host_session(session_id: Optional[str] = Header(None, alias="X-Session-ID")):
    """验证主持人 session"""
    if not session_id:
        raise HTTPException(status_code=401, detail="未授权")
    return session_id

@router.get("/status")
async def get_host_status(
    session_id: str = Depends(get_host_session),
    db: Session = Depends(get_db)
):
    """获取主持人控制面板状态"""
    # 验证 session
    participant = ParticipantService.get_participant_by_session(db, session_id)
    if not participant or participant.role != 'host':
        raise HTTPException(status_code=403, detail="无权限")
    
    activity = ActivityService.get_current_activity(db)
    if not activity:
        raise HTTPException(status_code=404, detail="没有活动")
    
    # 获取签到人数
    participant_count = ParticipantService.get_participants_count(db, activity.id)
    
    # 获取投票列表
    votes = VoteService.get_votes_by_activity(db, activity.id)
    vote_list = []
    for vote in votes:
        options = json.loads(vote.options) if vote.options else None
        vote_list.append({
            'id': vote.id,
            'title': vote.title,
            'type': vote.type,
            'options': options
        })
    
    return {
        'activity_id': activity.id,
        'activity_name': activity.name,
        'activity_status': activity.status,
        'participant_count': participant_count,
        'votes': vote_list
    }

@router.post("/activity/start")
async def start_activity(
    session_id: str = Depends(get_host_session),
    db: Session = Depends(get_db)
):
    """开始活动"""
    participant = ParticipantService.get_participant_by_session(db, session_id)
    if not participant or participant.role != 'host':
        raise HTTPException(status_code=403, detail="无权限")
    
    activity = ActivityService.get_current_activity(db)
    if not activity:
        raise HTTPException(status_code=404, detail="没有活动")
    
    # 更新活动状态
    ActivityService.update_activity_status(db, activity.id, 'active')
    
    # 广播活动开始
    await manager.broadcast({
        "type": "activity_started",
        "data": {"activity_name": activity.name}
    })
    
    return {"message": "活动已开始"}

@router.post("/vote/start")
async def start_vote(
    vote_id: int,
    session_id: str = Depends(get_host_session),
    db: Session = Depends(get_db)
):
    """开始投票"""
    participant = ParticipantService.get_participant_by_session(db, session_id)
    if not participant or participant.role != 'host':
        raise HTTPException(status_code=403, detail="无权限")
    
    vote = VoteService.get_vote(db, vote_id)
    if not vote:
        raise HTTPException(status_code=404, detail="投票不存在")
    
    # 解析选项
    options = json.loads(vote.options) if vote.options else None
    
    # 广播开始投票
    await manager.broadcast({
        "type": "vote_started",
        "data": {
            "vote_id": vote.id,
            "title": vote.title,
            "type": vote.type,
            "options": options
        }
    })
    
    return {"message": "投票已开始"}

@router.post("/vote/end")
async def end_vote(
    vote_id: int,
    session_id: str = Depends(get_host_session),
    db: Session = Depends(get_db)
):
    """结束投票并显示结果"""
    participant = ParticipantService.get_participant_by_session(db, session_id)
    if not participant or participant.role != 'host':
        raise HTTPException(status_code=403, detail="无权限")
    
    # 获取投票结果
    results = VoteService.get_vote_results(db, vote_id)
    
    # 广播投票结果
    await manager.broadcast({
        "type": "vote_ended",
        "data": results
    })
    
    return {"message": "投票已结束", "results": results}

@router.post("/vote/exit")
async def exit_vote(
    session_id: str = Depends(get_host_session),
    db: Session = Depends(get_db)
):
    """退出投票,回到签到页"""
    participant = ParticipantService.get_participant_by_session(db, session_id)
    if not participant or participant.role != 'host':
        raise HTTPException(status_code=403, detail="无权限")
    
    # 广播退出投票
    await manager.broadcast({
        "type": "vote_exited"
    })
    
    return {"message": "已退出投票"}

@router.post("/activity/end")
async def end_activity(
    session_id: str = Depends(get_host_session),
    db: Session = Depends(get_db)
):
    """结束活动,显示统计"""
    participant = ParticipantService.get_participant_by_session(db, session_id)
    if not participant or participant.role != 'host':
        raise HTTPException(status_code=403, detail="无权限")
    
    activity = ActivityService.get_current_activity(db)
    if not activity:
        raise HTTPException(status_code=404, detail="没有活动")
    
    # 获取活动统计
    summary = ActivityService.get_activity_summary(db, activity.id)
    
    # 更新活动状态
    ActivityService.update_activity_status(db, activity.id, 'ended')
    
    # 广播活动结束
    await manager.broadcast({
        "type": "activity_ended",
        "data": summary
    })
    
    return {"message": "活动已结束", "summary": summary}

@router.post("/activity/close")
async def close_activity(
    session_id: str = Depends(get_host_session),
    db: Session = Depends(get_db)
):
    """退出活动,保存数据并重置"""
    participant = ParticipantService.get_participant_by_session(db, session_id)
    if not participant or participant.role != 'host':
        raise HTTPException(status_code=403, detail="无权限")
    
    activity = ActivityService.get_current_activity(db)
    if not activity:
        raise HTTPException(status_code=404, detail="没有活动")
    
    # 导出数据
    records_file, stats_file = ExportService.export_activity_data(db, activity.id)
    
    # 重置活动数据
    ActivityService.reset_activity_data(db, activity.id)
    
    # 广播活动关闭
    await manager.broadcast({
        "type": "activity_closed"
    })
    
    return {
        "message": "活动已关闭,数据已保存",
        "files": {
            "records": records_file,
            "statistics": stats_file
        }
    }
