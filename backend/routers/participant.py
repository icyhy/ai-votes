"""
参会人 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import VoteSubmit
from backend.services import ParticipantService, VoteService
from typing import Optional

router = APIRouter(prefix="/api/participant", tags=["participant"])

def get_participant_session(session_id: Optional[str] = Header(None, alias="X-Session-ID")):
    """验证参会人 session"""
    if not session_id:
        raise HTTPException(status_code=401, detail="未授权")
    return session_id

@router.get("/status")
async def get_participant_status(
    session_id: str = Depends(get_participant_session),
    db: Session = Depends(get_db)
):
    """获取参会人状态"""
    participant = ParticipantService.get_participant_by_session(db, session_id)
    if not participant:
        raise HTTPException(status_code=404, detail="参会人不存在")
    
    return {
        'name': participant.name,
        'department': participant.department,
        'signed_in_at': participant.signed_in_at.isoformat()
    }

@router.post("/vote")
async def submit_vote(
    vote_submit: VoteSubmit,
    session_id: str = Depends(get_participant_session),
    db: Session = Depends(get_db)
):
    """提交投票"""
    participant = ParticipantService.get_participant_by_session(db, session_id)
    if not participant:
        raise HTTPException(status_code=404, detail="参会人不存在")
    
    # 提交投票
    record = VoteService.submit_vote(
        db,
        vote_submit.vote_id,
        participant.id,
        vote_submit.answer
    )
    
    return {"message": "投票已提交", "record_id": record.id}
