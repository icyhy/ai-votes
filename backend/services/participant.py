"""
参会人管理服务
"""
from sqlalchemy.orm import Session
from backend.models import Participant
from typing import Optional
import uuid

class ParticipantService:
    """参会人管理服务"""
    
    @staticmethod
    def create_participant(
        db: Session,
        activity_id: int,
        name: str,
        department: Optional[str],
        role: str
    ) -> Participant:
        """创建参会人(签到)"""
        session_id = str(uuid.uuid4())
        
        participant = Participant(
            activity_id=activity_id,
            name=name,
            department=department,
            role=role,
            session_id=session_id
        )
        db.add(participant)
        db.commit()
        db.refresh(participant)
        return participant
    
    @staticmethod
    def get_participant_by_session(db: Session, session_id: str) -> Optional[Participant]:
        """通过 session_id 获取参会人"""
        return db.query(Participant).filter(
            Participant.session_id == session_id
        ).first()
    
    @staticmethod
    def check_duplicate_signin(db: Session, activity_id: int, session_id: str) -> bool:
        """检查是否重复签到"""
        existing = db.query(Participant).filter(
            Participant.activity_id == activity_id,
            Participant.session_id == session_id
        ).first()
        return existing is not None
    
    @staticmethod
    def get_participants_count(db: Session, activity_id: int) -> int:
        """获取签到人数"""
        return db.query(Participant).filter(
            Participant.activity_id == activity_id
        ).count()
    
    @staticmethod
    def get_host(db: Session, activity_id: int) -> Optional[Participant]:
        """获取主持人"""
        return db.query(Participant).filter(
            Participant.activity_id == activity_id,
            Participant.role == 'host'
        ).first()
