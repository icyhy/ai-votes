"""
CSV 导出服务
"""
import csv
from pathlib import Path
from sqlalchemy.orm import Session
from backend.models import Activity, Vote, VoteRecord, Participant
from datetime import datetime
import json

class ExportService:
    """CSV 导出服务"""
    
    @staticmethod
    def export_activity_data(db: Session, activity_id: int) -> tuple[str, str]:
        """
        导出活动数据为 CSV 文件
        
        Args:
            db: 数据库会话
            activity_id: 活动 ID
        
        Returns:
            (投票记录文件路径, 统计结果文件路径)
        """
        activity = db.query(Activity).filter(Activity.id == activity_id).first()
        if not activity:
            return None, None
        
        # 确保导出目录存在
        export_dir = Path("data/exports")
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        records_file = export_dir / f"activity_{activity_id}_records_{timestamp}.csv"
        stats_file = export_dir / f"activity_{activity_id}_statistics_{timestamp}.csv"
        
        # 导出投票记录
        ExportService._export_vote_records(db, activity_id, records_file)
        
        # 导出统计结果
        ExportService._export_statistics(db, activity_id, stats_file)
        
        return str(records_file), str(stats_file)
    
    @staticmethod
    def _export_vote_records(db: Session, activity_id: int, filepath: Path):
        """导出投票记录"""
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow(['活动名称', '投票标题', '参会人姓名', '参会人部门', '投票内容', '投票时间'])
            
            # 获取活动信息
            activity = db.query(Activity).filter(Activity.id == activity_id).first()
            
            # 获取所有投票
            votes = db.query(Vote).filter(Vote.activity_id == activity_id).all()
            
            for vote in votes:
                # 获取该投票的所有记录
                records = db.query(VoteRecord).filter(VoteRecord.vote_id == vote.id).all()
                
                for record in records:
                    # 获取参会人信息
                    participant = db.query(Participant).filter(
                        Participant.id == record.participant_id
                    ).first()
                    
                    # 解析答案
                    answer = json.loads(record.answer)
                    answer_text = ExportService._format_answer(vote.type, answer)
                    
                    # 写入数据
                    writer.writerow([
                        activity.name,
                        vote.title,
                        participant.name if participant else '未知',
                        participant.department if participant and participant.department else '',
                        answer_text,
                        record.voted_at.strftime('%Y-%m-%d %H:%M:%S')
                    ])
    
    @staticmethod
    def _export_statistics(db: Session, activity_id: int, filepath: Path):
        """导出统计结果"""
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow(['投票标题', '选项', '票数', '百分比'])
            
            # 获取所有投票
            votes = db.query(Vote).filter(Vote.activity_id == activity_id).all()
            
            for vote in votes:
                records = db.query(VoteRecord).filter(VoteRecord.vote_id == vote.id).all()
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
                    
                    # 写入数据
                    for option, count in results.items():
                        percentage = f"{count / total_count * 100:.1f}%" if total_count > 0 else "0%"
                        writer.writerow([vote.title, option, count, percentage])
                
                elif vote.type == 'rating':
                    # 评分统计
                    ratings = [0] * 5
                    for record in records:
                        answer = json.loads(record.answer)
                        rating = answer.get('rating', 0)
                        if 1 <= rating <= 5:
                            ratings[rating - 1] += 1
                    
                    for i, count in enumerate(ratings):
                        percentage = f"{count / total_count * 100:.1f}%" if total_count > 0 else "0%"
                        writer.writerow([vote.title, f"{i + 1}星", count, percentage])
                    
                    # 计算平均分
                    total_rating = sum((i + 1) * count for i, count in enumerate(ratings))
                    avg_rating = total_rating / total_count if total_count > 0 else 0
                    writer.writerow([vote.title, "平均分", f"{avg_rating:.2f}", ""])
                
                elif vote.type == 'text':
                    # 问答题统计
                    writer.writerow([vote.title, f"共{total_count}条回答", total_count, "100%"])
    
    @staticmethod
    def _format_answer(vote_type: str, answer: dict) -> str:
        """格式化答案为字符串"""
        if vote_type == 'single':
            return answer.get('selected', '')
        elif vote_type == 'multiple':
            selected = answer.get('selected', [])
            return ', '.join(selected)
        elif vote_type == 'text':
            return answer.get('text', '')
        elif vote_type == 'rating':
            return f"{answer.get('rating', 0)}星"
        return ''
    
    @staticmethod
    def list_export_files() -> list:
        """列出所有导出的 CSV 文件"""
        export_dir = Path("data/exports")
        if not export_dir.exists():
            return []
        
        files = []
        for file in export_dir.glob("*.csv"):
            files.append({
                'filename': file.name,
                'created_at': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
            })
        
        # 按创建时间倒序排列
        files.sort(key=lambda x: x['created_at'], reverse=True)
        return files
