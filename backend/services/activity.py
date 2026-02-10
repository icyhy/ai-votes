"""
活动管理服务
"""
from sqlalchemy.orm import Session
from backend.models import Activity, Vote, Participant, VoteRecord
from backend.schemas import ActivityCreate, VoteCreate
from typing import Optional, List
import json

class ActivityService:
    """活动管理服务"""
    
    @staticmethod
    def create_activity(db: Session, activity: ActivityCreate) -> Activity:
        """创建新活动"""
        db_activity = Activity(
            name=activity.name,
            theme=activity.theme,
            status='pending'
        )
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
        
        # 自动从投票模板复制投票列表到新活动
        from backend.services.vote_template import VoteTemplateService
        VoteTemplateService.copy_templates_to_activity(db, db_activity.id)
        
        return db_activity
    
    @staticmethod
    def get_current_activity(db: Session) -> Optional[Activity]:
        """获取当前活动(最新的活动)"""
        return db.query(Activity).order_by(Activity.id.desc()).first()
    
    @staticmethod
    def update_activity_status(db: Session, activity_id: int, status: str) -> Activity:
        """更新活动状态"""
        activity = db.query(Activity).filter(Activity.id == activity_id).first()
        if activity:
            activity.status = status
            db.commit()
            db.refresh(activity)
        return activity
    
    @staticmethod
    def get_activity_summary(db: Session, activity_id: int) -> dict:
        """获取活动统计摘要"""
        # 签到人数
        total_participants = db.query(Participant).filter(
            Participant.activity_id == activity_id
        ).count()
        
        # 投票数量
        votes = db.query(Vote).filter(Vote.activity_id == activity_id).all()
        votes_completed = len(votes)
        
        # 每个投票的参与情况
        votes_summary = []
        for vote in votes:
            vote_count = db.query(VoteRecord).filter(
                VoteRecord.vote_id == vote.id
            ).count()
            votes_summary.append({
                'title': vote.title,
                'type': vote.type,
                'participants': vote_count
            })
        
        return {
            'total_participants': total_participants,
            'votes_completed': votes_completed,
            'votes_summary': votes_summary
        }
    
    @staticmethod
    def reset_activity_data(db: Session, activity_id: int):
        """重置活动数据(清空签到和投票记录)"""
        # 删除投票记录
        db.query(VoteRecord).filter(
            VoteRecord.vote_id.in_(
                db.query(Vote.id).filter(Vote.activity_id == activity_id)
            )
        ).delete(synchronize_session=False)
        
        # 删除参会人
        db.query(Participant).filter(
            Participant.activity_id == activity_id
        ).delete(synchronize_session=False)
        
        db.commit()
