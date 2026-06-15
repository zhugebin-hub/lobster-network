# -*- coding: utf-8 -*-
"""
题库管理模块
负责题库的加载、保存和管理
"""

import json
import os
from typing import Dict, List, Any


class QuestionDatabase:
    """题库数据库类"""
    
    def __init__(self, db_path: str = "questions.json"):
        """
        初始化题库
        
        Args:
            db_path: 题库文件路径
        """
        self.db_path = db_path
        self.questions = {
            "single_choice": [],  # 单选题
            "multiple_choice": [],  # 多选题
            "true_false": []  # 判断题
        }
        self.load()
    
    def load(self) -> bool:
        """
        加载题库
        
        Returns:
            是否加载成功
        """
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.questions = data
                return True
            else:
                # 如果文件不存在，创建默认题库
                self.create_default_questions()
                self.save()
                return True
        except Exception as e:
            print(f"加载题库失败：{e}")
            return False
    
    def save(self) -> bool:
        """
        保存题库
        
        Returns:
            是否保存成功
        """
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.questions, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存题库失败：{e}")
            return False
    
    def create_default_questions(self):
        """创建默认题库（50 道题）"""
        # 单选题 30 题
        self.questions["single_choice"] = [
            {
                "id": 1,
                "question": "计算机中用来表示信息的最小单位是？",
                "options": ["A. 字节", "B. 位", "C. 字", "D. 双字"],
                "answer": "B",
                "category": "计算机基础"
            },
            {
                "id": 2,
                "question": "1KB 等于多少字节？",
                "options": ["A. 1000", "B. 1024", "C. 512", "D. 2048"],
                "answer": "B",
                "category": "计算机基础"
            },
            {
                "id": 3,
                "question": "CPU 的主要功能是？",
                "options": ["A. 存储数据", "B. 处理数据", "C. 显示图像", "D. 播放声音"],
                "answer": "B",
                "category": "计算机基础"
            },
            {
                "id": 4,
                "question": "Windows 操作系统属于？",
                "options": ["A. 应用软件", "B. 系统软件", "C. 工具软件", "D. 杀毒软件"],
                "answer": "B",
                "category": "Windows 操作"
            },
            {
                "id": 5,
                "question": "在 Windows 中，复制文件的快捷键是？",
                "options": ["A. Ctrl+X", "B. Ctrl+C", "C. Ctrl+V", "D. Ctrl+Z"],
                "answer": "B",
                "category": "Windows 操作"
            },
            {
                "id": 6,
                "question": "Windows 资源管理器的作用是？",
                "options": ["A. 管理文件", "B. 播放音乐", "C. 编辑文档", "D. 上网浏览"],
                "answer": "A",
                "category": "Windows 操作"
            },
            {
                "id": 7,
                "question": "IP 地址由几部分组成？",
                "options": ["A. 2 部分", "B. 3 部分", "C. 4 部分", "D. 5 部分"],
                "answer": "C",
                "category": "网络基础"
            },
            {
                "id": 8,
                "question": "HTTP 协议默认使用的端口号是？",
                "options": ["A. 21", "B. 25", "C. 80", "D. 443"],
                "answer": "C",
                "category": "网络基础"
            },
            {
                "id": 9,
                "question": "下列哪个是合法的电子邮件地址？",
                "options": ["A. user@example", "B. user@example.com", "C. @example.com", "D. user@"],
                "answer": "B",
                "category": "网络基础"
            },
            {
                "id": 10,
                "question": "计算机病毒的本质是？",
                "options": ["A. 细菌", "B. 程序", "C. 硬件", "D. 文件"],
                "answer": "B",
                "category": "信息安全"
            },
            {
                "id": 11,
                "question": "以下哪种密码最安全？",
                "options": ["A. 123456", "B. abcdef", "C. Abc@123456", "D. 888888"],
                "answer": "C",
                "category": "信息安全"
            },
            {
                "id": 12,
                "question": "防火墙的主要作用是？",
                "options": ["A. 防止火灾", "B. 网络安全防护", "C. 加速网络", "D. 存储数据"],
                "answer": "B",
                "category": "信息安全"
            },
            {
                "id": 13,
                "question": "Word 文档的默认扩展名是？",
                "options": ["A. .txt", "B. .docx", "C. .pdf", "D. .wps"],
                "answer": "B",
                "category": "Office 应用"
            },
            {
                "id": 14,
                "question": "在 Excel 中，求和函数的名称是？",
                "options": ["A. COUNT", "B. AVERAGE", "C. SUM", "D. MAX"],
                "answer": "C",
                "category": "Office 应用"
            },
            {
                "id": 15,
                "question": "PowerPoint 主要用于制作？",
                "options": ["A. 文档", "B. 表格", "C. 演示文稿", "D. 数据库"],
                "answer": "C",
                "category": "Office 应用"
            },
            {
                "id": 16,
                "question": "RAM 的特点是？",
                "options": ["A. 断电后数据丢失", "B. 断电后数据保留", "C. 只能读取", "D. 速度慢"],
                "answer": "A",
                "category": "计算机基础"
            },
            {
                "id": 17,
                "question": "下列不属于输入设备的是？",
                "options": ["A. 键盘", "B. 鼠标", "C. 显示器", "D. 扫描仪"],
                "answer": "C",
                "category": "计算机基础"
            },
            {
                "id": 18,
                "question": "Windows 中，关闭当前窗口的快捷键是？",
                "options": ["A. Alt+F4", "B. Ctrl+F4", "C. Alt+Tab", "D. Ctrl+Esc"],
                "answer": "A",
                "category": "Windows 操作"
            },
            {
                "id": 19,
                "question": "DNS 服务器的作用是？",
                "options": ["A. 分配 IP 地址", "B. 域名解析", "C. 发送邮件", "D. 传输文件"],
                "answer": "B",
                "category": "网络基础"
            },
            {
                "id": 20,
                "question": "下列属于无线网络标准的是？",
                "options": ["A. IEEE 802.3", "B. IEEE 802.11", "C. IEEE 802.1", "D. IEEE 802.5"],
                "answer": "B",
                "category": "网络基础"
            },
            {
                "id": 21,
                "question": "黑客是指？",
                "options": ["A. 穿黑衣的人", "B. 网络攻击者", "C. 网络管理员", "D. 程序员"],
                "answer": "B",
                "category": "信息安全"
            },
            {
                "id": 22,
                "question": "在 Word 中，设置字体格式的菜单是？",
                "options": ["A. 文件", "B. 开始", "C. 插入", "D. 视图"],
                "answer": "B",
                "category": "Office 应用"
            },
            {
                "id": 23,
                "question": "Excel 中单元格的地址表示方式是？",
                "options": ["A. 列号行号", "B. 行号列号", "C. 数字", "D. 字母"],
                "answer": "A",
                "category": "Office 应用"
            },
            {
                "id": 24,
                "question": "二进制数 1010 转换为十进制是？",
                "options": ["A. 8", "B. 9", "C. 10", "D. 11"],
                "answer": "C",
                "category": "计算机基础"
            },
            {
                "id": 25,
                "question": "操作系统的主要功能不包括？",
                "options": ["A. 处理器管理", "B. 存储管理", "C. 文件管理", "D. 游戏娱乐"],
                "answer": "D",
                "category": "计算机基础"
            },
            {
                "id": 26,
                "question": "Windows 任务栏的作用是？",
                "options": ["A. 显示时间", "B. 切换程序", "C. 播放音乐", "D. 存储文件"],
                "answer": "B",
                "category": "Windows 操作"
            },
            {
                "id": 27,
                "question": "URL 的含义是？",
                "options": ["A. 统一资源定位符", "B. 统一资源管理器", "C. 通用资源列表", "D. 全球资源定位"],
                "answer": "A",
                "category": "网络基础"
            },
            {
                "id": 28,
                "question": "下列不属于计算机病毒传播途径的是？",
                "options": ["A. U 盘", "B. 网络", "C. 电子邮件", "D. 空气"],
                "answer": "D",
                "category": "信息安全"
            },
            {
                "id": 29,
                "question": "在 Excel 中，公式必须以什么符号开头？",
                "options": ["A. +", "B. -", "C. =", "D. /"],
                "answer": "C",
                "category": "Office 应用"
            },
            {
                "id": 30,
                "question": "计算机的发展经历了几个时代？",
                "options": ["A. 3 个", "B. 4 个", "C. 5 个", "D. 6 个"],
                "answer": "B",
                "category": "计算机基础"
            }
        ]
        
        # 多选题 10 题
        self.questions["multiple_choice"] = [
            {
                "id": 31,
                "question": "下列属于计算机硬件的是？（多选）",
                "options": ["A. CPU", "B. 内存", "C. Windows", "D. 硬盘"],
                "answer": "ABD",
                "category": "计算机基础"
            },
            {
                "id": 32,
                "question": "Windows 操作系统支持的文件系统有？（多选）",
                "options": ["A. FAT32", "B. NTFS", "C. ext4", "D. exFAT"],
                "answer": "ABD",
                "category": "Windows 操作"
            },
            {
                "id": 33,
                "question": "下列属于网络协议的有？（多选）",
                "options": ["A. TCP", "B. IP", "C. HTTP", "D. USB"],
                "answer": "ABC",
                "category": "网络基础"
            },
            {
                "id": 34,
                "question": "信息安全的基本属性包括？（多选）",
                "options": ["A. 机密性", "B. 完整性", "C. 可用性", "D. 可复制性"],
                "answer": "ABC",
                "category": "信息安全"
            },
            {
                "id": 35,
                "question": "Office 套件包括？（多选）",
                "options": ["A. Word", "B. Excel", "C. Photoshop", "D. PowerPoint"],
                "answer": "ABD",
                "category": "Office 应用"
            },
            {
                "id": 36,
                "question": "下列属于输入设备的有？（多选）",
                "options": ["A. 键盘", "B. 鼠标", "C. 打印机", "D. 扫描仪"],
                "answer": "ABD",
                "category": "计算机基础"
            },
            {
                "id": 37,
                "question": "常见的网络拓扑结构有？（多选）",
                "options": ["A. 星型", "B. 总线型", "C. 环型", "D. 三角型"],
                "answer": "ABC",
                "category": "网络基础"
            },
            {
                "id": 38,
                "question": "防范计算机病毒的措施有？（多选）",
                "options": ["A. 安装杀毒软件", "B. 不打开陌生邮件", "C. 定期更新系统", "D. 随意下载软件"],
                "answer": "ABC",
                "category": "信息安全"
            },
            {
                "id": 39,
                "question": "Excel 中的图表类型包括？（多选）",
                "options": ["A. 柱形图", "B. 折线图", "C. 饼图", "D. 散点图"],
                "answer": "ABCD",
                "category": "Office 应用"
            },
            {
                "id": 40,
                "question": "下列存储设备中，断电后数据不会丢失的有？（多选）",
                "options": ["A. 硬盘", "B. U 盘", "C. RAM", "D. ROM"],
                "answer": "ABD",
                "category": "计算机基础"
            }
        ]
        
        # 判断题 10 题
        self.questions["true_false"] = [
            {
                "id": 41,
                "question": "计算机只能处理数字信息。",
                "options": ["正确", "错误"],
                "answer": "错误",
                "category": "计算机基础"
            },
            {
                "id": 42,
                "question": "Windows 是开源操作系统。",
                "options": ["正确", "错误"],
                "answer": "错误",
                "category": "Windows 操作"
            },
            {
                "id": 43,
                "question": "IP 地址是唯一的。",
                "options": ["正确", "错误"],
                "answer": "正确",
                "category": "网络基础"
            },
            {
                "id": 44,
                "question": "防火墙可以完全防止所有网络攻击。",
                "options": ["正确", "错误"],
                "answer": "错误",
                "category": "信息安全"
            },
            {
                "id": 45,
                "question": "Word 可以编辑表格。",
                "options": ["正确", "错误"],
                "answer": "正确",
                "category": "Office 应用"
            },
            {
                "id": 46,
                "question": "1GB 等于 1000MB。",
                "options": ["正确", "错误"],
                "answer": "错误",
                "category": "计算机基础"
            },
            {
                "id": 47,
                "question": "回收站中的文件可以被恢复。",
                "options": ["正确", "错误"],
                "answer": "正确",
                "category": "Windows 操作"
            },
            {
                "id": 48,
                "question": "HTTPS 比 HTTP 更安全。",
                "options": ["正确", "错误"],
                "answer": "正确",
                "category": "网络基础"
            },
            {
                "id": 49,
                "question": "密码越复杂越安全。",
                "options": ["正确", "错误"],
                "answer": "正确",
                "category": "信息安全"
            },
            {
                "id": 50,
                "question": "Excel 不能进行数据排序。",
                "options": ["正确", "错误"],
                "answer": "错误",
                "category": "Office 应用"
            }
        ]
    
    def get_questions(self, question_type: str) -> List[Dict[str, Any]]:
        """
        获取指定类型的题目
        
        Args:
            question_type: 题目类型（single_choice/multiple_choice/true_false）
        
        Returns:
            题目列表
        """
        return self.questions.get(question_type, [])
    
    def get_all_questions(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取所有题目
        
        Returns:
            所有题目
        """
        return self.questions
    
    def add_question(self, question_type: str, question: Dict[str, Any]) -> bool:
        """
        添加题目
        
        Args:
            question_type: 题目类型
            question: 题目数据
        
        Returns:
            是否添加成功
        """
        try:
            if question_type not in self.questions:
                return False
            self.questions[question_type].append(question)
            return self.save()
        except Exception as e:
            print(f"添加题目失败：{e}")
            return False
    
    def delete_question(self, question_type: str, question_id: int) -> bool:
        """
        删除题目
        
        Args:
            question_type: 题目类型
            question_id: 题目 ID
        
        Returns:
            是否删除成功
        """
        try:
            questions = self.questions.get(question_type, [])
            for i, q in enumerate(questions):
                if q.get("id") == question_id:
                    questions.pop(i)
                    return self.save()
            return False
        except Exception as e:
            print(f"删除题目失败：{e}")
            return False
    
    def update_question(self, question_type: str, question_id: int, 
                       new_question: Dict[str, Any]) -> bool:
        """
        更新题目
        
        Args:
            question_type: 题目类型
            question_id: 题目 ID
            new_question: 新题目数据
        
        Returns:
            是否更新成功
        """
        try:
            questions = self.questions.get(question_type, [])
            for i, q in enumerate(questions):
                if q.get("id") == question_id:
                    questions[i] = new_question
                    return self.save()
            return False
        except Exception as e:
            print(f"更新题目失败：{e}")
            return False
    
    def get_question_count(self, question_type: str) -> int:
        """
        获取指定类型的题目数量
        
        Args:
            question_type: 题目类型
        
        Returns:
            题目数量
        """
        return len(self.questions.get(question_type, 0))
    
    def get_total_count(self) -> int:
        """
        获取总题目数
        
        Returns:
            总题目数
        """
        total = 0
        for questions in self.questions.values():
            total += len(questions)
        return total
