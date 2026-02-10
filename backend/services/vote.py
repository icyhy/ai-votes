"""
投票管理服务
"""
from sqlalchemy.orm import Session
from backend.models import Vote, VoteRecord, Participant
from backend.schemas import VoteCreate, VoteUpdate
from typing import List, Optional
import json

class VoteService:
    """投票管理服务"""
    
    @staticmethod
    def create_vote(db: Session, vote: VoteCreate) -> Vote:
        """创建投票"""
        # 将选项列表转换为 JSON 字符串
        options_json = json.dumps(vote.options, ensure_ascii=False) if vote.options else None
        
        db_vote = Vote(
            activity_id=vote.activity_id,
            title=vote.title,
            type=vote.type,
            options=options_json,
            order_index=vote.order_index
        )
        db.add(db_vote)
        db.commit()
        db.refresh(db_vote)
        return db_vote
    
    @staticmethod
    def get_vote(db: Session, vote_id: int) -> Optional[Vote]:
        """获取投票"""
        return db.query(Vote).filter(Vote.id == vote_id).first()
    
    @staticmethod
    def get_votes_by_activity(db: Session, activity_id: int) -> List[Vote]:
        """获取活动的所有投票"""
        return db.query(Vote).filter(
            Vote.activity_id == activity_id
        ).order_by(Vote.order_index).all()
    
    @staticmethod
    def update_vote(db: Session, vote_id: int, vote_update: VoteUpdate) -> Optional[Vote]:
        """更新投票"""
        db_vote = db.query(Vote).filter(Vote.id == vote_id).first()
        if not db_vote:
            return None
        
        if vote_update.title:
            db_vote.title = vote_update.title
        if vote_update.type:
            db_vote.type = vote_update.type
        if vote_update.options is not None:
            db_vote.options = json.dumps(vote_update.options, ensure_ascii=False)
        if vote_update.order_index is not None:
            db_vote.order_index = vote_update.order_index
        
        db.commit()
        db.refresh(db_vote)
        return db_vote
    
    @staticmethod
    def delete_vote(db: Session, vote_id: int) -> bool:
        """删除投票"""
        db_vote = db.query(Vote).filter(Vote.id == vote_id).first()
        if not db_vote:
            return False
        
        # 先删除相关的投票记录
        db.query(VoteRecord).filter(VoteRecord.vote_id == vote_id).delete()
        
        db.delete(db_vote)
        db.commit()
        return True
    
    @staticmethod
    def submit_vote(db: Session, vote_id: int, participant_id: int, answer: dict) -> VoteRecord:
        """提交投票"""
        # 检查是否已经投过票
        existing = db.query(VoteRecord).filter(
            VoteRecord.vote_id == vote_id,
            VoteRecord.participant_id == participant_id
        ).first()
        
        if existing:
            # 更新答案
            existing.answer = json.dumps(answer, ensure_ascii=False)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # 创建新记录
            record = VoteRecord(
                vote_id=vote_id,
                participant_id=participant_id,
                answer=json.dumps(answer, ensure_ascii=False)
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
    
    @staticmethod
    def get_vote_results(db: Session, vote_id: int) -> dict:
        """获取投票结果统计"""
        vote = db.query(Vote).filter(Vote.id == vote_id).first()
        if not vote:
            return {}
        
        records = db.query(VoteRecord).filter(VoteRecord.vote_id == vote_id).all()
        total_count = len(records)
        
        if vote.type in ['single', 'multiple']:
            # 单选/多选统计
            options = json.loads(vote.options) if vote.options else []
            results = {option: 0 for option in options}
            
            for record in records:
                answer = json.loads(record.answer)
                if vote.type == 'single':
                    selected = answer.get('selected')
                    if selected in results:
                        results[selected] += 1
                else:  # multiple
                    selected_list = answer.get('selected', [])
                    for option in selected_list:
                        if option in results:
                            results[option] += 1
            
            # 转换为列表格式
            result_list = []
            for option, count in results.items():
                percentage = f"{count / total_count * 100:.1f}%" if total_count > 0 else "0%"
                result_list.append({
                    'option': option,
                    'count': count,
                    'percentage': percentage
                })
            
            return {
                'vote_id': vote_id,
                'type': vote.type,
                'results': result_list
            }
        
        elif vote.type == 'rating':
            # 评分统计
            ratings = [0] * 5  # 1-5 分
            for record in records:
                answer = json.loads(record.answer)
                rating = answer.get('rating', 0)
                if 1 <= rating <= 5:
                    ratings[rating - 1] += 1
            
            result_list = []
            for i, count in enumerate(ratings):
                percentage = f"{count / total_count * 100:.1f}%" if total_count > 0 else "0%"
                result_list.append({
                    'option': f"{i + 1}星",
                    'count': count,
                    'percentage': percentage
                })
            
            # 计算平均分
            total_rating = sum((i + 1) * count for i, count in enumerate(ratings))
            avg_rating = total_rating / total_count if total_count > 0 else 0
            
            return {
                'vote_id': vote_id,
                'type': vote.type,
                'results': result_list,
                'average': round(avg_rating, 2)
            }
        
        elif vote.type == 'text':
            # 问答题返回所有答案
            answers = []
            for record in records:
                answer = json.loads(record.answer)
                participant = db.query(Participant).filter(
                    Participant.id == record.participant_id
                ).first()
                answers.append({
                    'participant': participant.name if participant else '匿名',
                    'text': answer.get('text', '')
                })
            
            return {
                'vote_id': vote_id,
                'type': vote.type,
                'total_count': total_count,
                'answers': answers
            }
        
        return {}
