"""
投票模板管理服务
"""
from sqlalchemy.orm import Session
from backend.models import VoteTemplate, Vote
from typing import List, Optional
import json

class VoteTemplateService:
    """投票模板管理服务"""
    
    @staticmethod
    def create_template(db: Session, title: str, type: str, options: list = None, order_index: int = None) -> VoteTemplate:
        """创建投票模板"""
        options_json = json.dumps(options, ensure_ascii=False) if options else None
        
        db_template = VoteTemplate(
            title=title,
            type=type,
            options=options_json,
            order_index=order_index
        )
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        return db_template
    
    @staticmethod
    def get_all_templates(db: Session) -> List[VoteTemplate]:
        """获取所有投票模板"""
        return db.query(VoteTemplate).order_by(VoteTemplate.order_index).all()
    
    @staticmethod
    def get_template(db: Session, template_id: int) -> Optional[VoteTemplate]:
        """获取单个投票模板"""
        return db.query(VoteTemplate).filter(VoteTemplate.id == template_id).first()
    
    @staticmethod
    def update_template(db: Session, template_id: int, title: str = None, type: str = None, 
                       options: list = None, order_index: int = None) -> Optional[VoteTemplate]:
        """更新投票模板"""
        db_template = db.query(VoteTemplate).filter(VoteTemplate.id == template_id).first()
        if not db_template:
            return None
        
        if title is not None:
            db_template.title = title
        if type is not None:
            db_template.type = type
        if options is not None:
            db_template.options = json.dumps(options, ensure_ascii=False)
        if order_index is not None:
            db_template.order_index = order_index
        
        db.commit()
        db.refresh(db_template)
        return db_template
    
    @staticmethod
    def delete_template(db: Session, template_id: int) -> bool:
        """删除投票模板"""
        db_template = db.query(VoteTemplate).filter(VoteTemplate.id == template_id).first()
        if not db_template:
            return False
        
        db.delete(db_template)
        db.commit()
        return True
    
    @staticmethod
    def copy_templates_to_activity(db: Session, activity_id: int) -> List[Vote]:
        """将所有投票模板复制为活动投票列表"""
        templates = VoteTemplateService.get_all_templates(db)
        votes = []
        
        for template in templates:
            vote = Vote(
                activity_id=activity_id,
                title=template.title,
                type=template.type,
                options=template.options,
                order_index=template.order_index
            )
            db.add(vote)
            votes.append(vote)
        
        db.commit()
        return votes
