# -*- coding: utf-8 -*-
"""
成绩管理模块
负责成绩的记录、查询和导出
"""

import csv
import os
from datetime import datetime
from typing import Dict, List, Any


class ScoreManager:
    """成绩管理类"""
    
    def __init__(self, score_file: str = "scores.csv"):
        """
        初始化成绩管理器
        
        Args:
            score_file: 成绩文件路径
        """
        self.score_file = score_file
        self._init_file()
    
    def _init_file(self):
        """初始化成绩文件"""
        if not os.path.exists(self.score_file):
            with open(self.score_file, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "姓名", "班级", "身份证号", "考试日期", "考试时间",
                    "单选题得分", "多选题得分", "判断题得分", "总分"
                ])
    
    def save_score(self, student_info: Dict[str, str], scores: Dict[str, Any]) -> bool:
        """
        保存成绩
        
        Args:
            student_info: 学生信息（姓名、班级、身份证号）
            scores: 成绩信息（各题型得分和总分）
        
        Returns:
            是否保存成功
        """
        try:
            now = datetime.now()
            with open(self.score_file, 'a', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    student_info.get("name", ""),
                    student_info.get("class_name", ""),
                    student_info.get("id_number", ""),
                    now.strftime("%Y-%m-%d"),
                    now.strftime("%H:%M:%S"),
                    scores.get("single_score", 0),
                    scores.get("multiple_score", 0),
                    scores.get("true_false_score", 0),
                    scores.get("total_score", 0)
                ])
            return True
        except Exception as e:
            print(f"保存成绩失败：{e}")
            return False
    
    def get_all_scores(self) -> List[Dict[str, Any]]:
        """
        获取所有成绩记录
        
        Returns:
            成绩记录列表
        """
        scores = []
        try:
            if os.path.exists(self.score_file):
                with open(self.score_file, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        scores.append(row)
        except Exception as e:
            print(f"读取成绩失败：{e}")
        return scores
    
    def get_student_scores(self, id_number: str) -> List[Dict[str, Any]]:
        """
        获取指定学生的所有成绩
        
        Args:
            id_number: 身份证号
        
        Returns:
            成绩记录列表
        """
        all_scores = self.get_all_scores()
        return [s for s in all_scores if s.get("身份证号") == id_number]
    
    def get_scores_by_date(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        按日期范围获取成绩
        
        Args:
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
        
        Returns:
            成绩记录列表
        """
        all_scores = self.get_all_scores()
        
        if not start_date and not end_date:
            return all_scores
        
        filtered = []
        for score in all_scores:
            exam_date = score.get("考试日期", "")
            if start_date and exam_date < start_date:
                continue
            if end_date and exam_date > end_date:
                continue
            filtered.append(score)
        
        return filtered
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取成绩统计信息
        
        Returns:
            统计信息字典
        """
        all_scores = self.get_all_scores()
        
        if not all_scores:
            return {
                "total_count": 0,
                "average_score": 0,
                "max_score": 0,
                "min_score": 0,
                "pass_rate": 0
            }
        
        total_count = len(all_scores)
        total_scores = []
        pass_count = 0
        
        for score in all_scores:
            try:
                s = float(score.get("总分", 0))
                total_scores.append(s)
                if s >= 60:
                    pass_count += 1
            except:
                continue
        
        if not total_scores:
            return {
                "total_count": 0,
                "average_score": 0,
                "max_score": 0,
                "min_score": 0,
                "pass_rate": 0
            }
        
        return {
            "total_count": total_count,
            "average_score": sum(total_scores) / len(total_scores),
            "max_score": max(total_scores),
            "min_score": min(total_scores),
            "pass_rate": (pass_count / total_count) * 100
        }
    
    def export_to_excel(self, output_file: str = None) -> bool:
        """
        导出成绩到 Excel（需要 pandas）
        
        Args:
            output_file: 输出文件路径
        
        Returns:
            是否导出成功
        """
        try:
            import pandas as pd
            
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"成绩导出_{timestamp}.xlsx"
            
            all_scores = self.get_all_scores()
            
            if not all_scores:
                print("没有成绩数据可导出")
                return False
            
            df = pd.DataFrame(all_scores)
            df.to_excel(output_file, index=False, engine='openpyxl')
            print(f"成绩已导出到：{output_file}")
            return True
        except ImportError:
            print("未安装 pandas，无法导出 Excel 格式")
            print("请运行：pip install pandas openpyxl")
            return False
        except Exception as e:
            print(f"导出 Excel 失败：{e}")
            return False
    
    def delete_score(self, index: int) -> bool:
        """
        删除指定索引的成绩记录
        
        Args:
            index: 记录索引（从 0 开始）
        
        Returns:
            是否删除成功
        """
        try:
            all_scores = self.get_all_scores()
            
            if index < 0 or index >= len(all_scores):
                return False
            
            all_scores.pop(index)
            
            # 重写文件
            with open(self.score_file, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "姓名", "班级", "身份证号", "考试日期", "考试时间",
                    "单选题得分", "多选题得分", "判断题得分", "总分"
                ])
                for score in all_scores:
                    writer.writerow([
                        score.get("姓名", ""),
                        score.get("班级", ""),
                        score.get("身份证号", ""),
                        score.get("考试日期", ""),
                        score.get("考试时间", ""),
                        score.get("单选题得分", ""),
                        score.get("多选题得分", ""),
                        score.get("判断题得分", ""),
                        score.get("总分", "")
                    ])
            return True
        except Exception as e:
            print(f"删除成绩失败：{e}")
            return False
