"""
龙虾网络 Manus 集成
支持：创建任务、管理文件、接收结果

用法：
    manus = ManusIntegration(api_key="your_api_key")
    
    # 创建任务
    task = manus.create_task(
        title="第一章 绪论动画演示",
        content="创建网络技术演进动画",
    )
    
    # 检查任务状态
    status = manus.get_task_status(task_id)
    
    # 获取任务结果
    result = manus.get_task_result(task_id)
"""

import json
import os
import time
import requests
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path

logger = None

def _get_logger():
    global logger
    if logger is None:
        try:
            from .utils.logger import get_logger
            logger = get_logger(__name__)
        except ImportError:
            import logging
            logger = logging.getLogger(__name__)
    return logger


@dataclass
class ManusTask:
    """Manus 任务"""
    task_id: str
    title: str
    status: str
    created_at: str
    task_url: Optional[str] = None
    share_url: Optional[str] = None
    share_visibility: str = "private"


@dataclass
class ManusFile:
    """Manus 文件"""
    file_id: str
    status: str
    size: int
    expires_at: str
    upload_url: Optional[str] = None


class ManusIntegration:
    """龙虾网络 Manus 集成"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.manus.ai",
        node_id: str = "lobster-001",
    ):
        """
        Args:
            api_key: Manus API Key
            base_url: Manus API Base URL
            node_id: 龙虾节点 ID
        """
        self.api_key = api_key
        self.base_url = base_url
        self.node_id = node_id
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })
    
    def create_task(
        self,
        title: str,
        content: str,
        project_id: Optional[str] = None,
        locale: str = "zh-CN",
        interactive_mode: bool = False,
        hide_in_task_list: bool = False,
        share_visibility: str = "private",
        agent_profile: str = "manus-1.6",
        structured_output_schema: Optional[dict] = None,
    ) -> ManusTask:
        """
        创建 Manus 任务
        
        Args:
            title: 任务标题
            content: 任务内容
            project_id: 项目 ID
            locale: 语言环境
            interactive_mode: 交互模式
            hide_in_task_list: 隐藏任务
            share_visibility: 分享可见性
            agent_profile: Agent 配置
            structured_output_schema: 结构化输出 Schema
        
        Returns:
            ManusTask
        """
        url = f"{self.base_url}/v2/task.create"
        
        payload = {
            "message": {
                "content": content,
            },
            "title": title,
            "locale": locale,
            "interactive_mode": interactive_mode,
            "hide_in_task_list": hide_in_task_list,
            "share_visibility": share_visibility,
            "agent_profile": agent_profile,
        }
        
        if project_id:
            payload["project_id"] = project_id
        
        if structured_output_schema:
            payload["structured_output_schema"] = structured_output_schema
        
        try:
            resp = self.session.post(url, json=payload)
            resp.raise_for_status()
            
            data = resp.json()
            if data.get("ok"):
                task = ManusTask(
                    task_id=data["task_id"],
                    title=data.get("task_title", title),
                    status="created",
                    created_at=datetime.utcnow().isoformat() + "Z",
                    task_url=data.get("task_url"),
                    share_url=data.get("share_url"),
                    share_visibility=data.get("share_visibility", "private"),
                )
                _get_logger().info(f"创建 Manus 任务成功: {task.task_id}")
                return task
            else:
                error = data.get("error", {})
                raise Exception(f"Manus API 错误: {error.get('code')} - {error.get('message')}")
        
        except Exception as e:
            _get_logger().error(f"创建 Manus 任务失败: {e}")
            raise
    
    def get_task_status(self, task_id: str) -> dict:
        """
        获取任务状态
        
        Args:
            task_id: 任务 ID
        
        Returns:
            任务状态
        """
        url = f"{self.base_url}/v2/task.detail"
        
        try:
            resp = self.session.post(url, json={"task_id": task_id})
            resp.raise_for_status()
            
            data = resp.json()
            if data.get("ok"):
                return data
            else:
                error = data.get("error", {})
                raise Exception(f"Manus API 错误: {error.get('code')} - {error.get('message')}")
        
        except Exception as e:
            _get_logger().error(f"获取任务状态失败: {e}")
            raise
    
    def get_task_messages(self, task_id: str, cursor: Optional[str] = None) -> dict:
        """
        获取任务消息
        
        Args:
            task_id: 任务 ID
            cursor: 分页游标
        
        Returns:
            任务消息列表
        """
        url = f"{self.base_url}/v2/task.listMessages"
        
        payload = {"task_id": task_id}
        if cursor:
            payload["cursor"] = cursor
        
        try:
            resp = self.session.post(url, json=payload)
            resp.raise_for_status()
            
            data = resp.json()
            if data.get("ok"):
                return data
            else:
                error = data.get("error", {})
                raise Exception(f"Manus API 错误: {error.get('code')} - {error.get('message')}")
        
        except Exception as e:
            _get_logger().error(f"获取任务消息失败: {e}")
            raise
    
    def send_message(self, task_id: str, content: str) -> dict:
        """
        发送消息
        
        Args:
            task_id: 任务 ID
            content: 消息内容
        
        Returns:
            响应数据
        """
        url = f"{self.base_url}/v2/task.sendMessage"
        
        payload = {
            "task_id": task_id,
            "message": {
                "content": content,
            },
        }
        
        try:
            resp = self.session.post(url, json=payload)
            resp.raise_for_status()
            
            data = resp.json()
            if data.get("ok"):
                return data
            else:
                error = data.get("error", {})
                raise Exception(f"Manus API 错误: {error.get('code')} - {error.get('message')}")
        
        except Exception as e:
            _get_logger().error(f"发送消息失败: {e}")
            raise
    
    def stop_task(self, task_id: str) -> dict:
        """
        停止任务
        
        Args:
            task_id: 任务 ID
        
        Returns:
            响应数据
        """
        url = f"{self.base_url}/v2/task.stop"
        
        payload = {"task_id": task_id}
        
        try:
            resp = self.session.post(url, json=payload)
            resp.raise_for_status()
            
            data = resp.json()
            if data.get("ok"):
                return data
            else:
                error = data.get("error", {})
                raise Exception(f"Manus API 错误: {error.get('code')} - {error.get('message')}")
        
        except Exception as e:
            _get_logger().error(f"停止任务失败: {e}")
            raise
    
    def delete_task(self, task_id: str) -> dict:
        """
        删除任务
        
        Args:
            task_id: 任务 ID
        
        Returns:
            响应数据
        """
        url = f"{self.base_url}/v2/task.delete"
        
        payload = {"task_id": task_id}
        
        try:
            resp = self.session.post(url, json=payload)
            resp.raise_for_status()
            
            data = resp.json()
            if data.get("ok"):
                return data
            else:
                error = data.get("error", {})
                raise Exception(f"Manus API 错误: {error.get('code')} - {error.get('message')}")
        
        except Exception as e:
            _get_logger().error(f"删除任务失败: {e}")
            raise
    
    def upload_file(self, file_path: str) -> ManusFile:
        """
        上传文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            ManusFile
        """
        url = f"{self.base_url}/v2/file.upload"
        
        try:
            # 创建文件记录
            resp = self.session.post(url, json={})
            resp.raise_for_status()
            
            data = resp.json()
            if not data.get("ok"):
                error = data.get("error", {})
                raise Exception(f"Manus API 错误: {error.get('code')} - {error.get('message')}")
            
            file_id = data["file"]["id"]
            upload_url = data["file"]["upload_url"]
            
            # 上传文件内容
            with open(file_path, "rb") as f:
                file_content = f.read()
            
            upload_resp = requests.put(upload_url, data=file_content)
            upload_resp.raise_for_status()
            
            file_info = ManusFile(
                file_id=file_id,
                status="uploaded",
                size=len(file_content),
                expires_at=data["file"].get("expires_at", ""),
                upload_url=upload_url,
            )
            
            _get_logger().info(f"上传文件成功: {file_id}")
            return file_info
        
        except Exception as e:
            _get_logger().error(f"上传文件失败: {e}")
            raise
    
    def create_animation_task(
        self,
        chapter: int,
        title: str,
        content: str,
        animation_type: str = "react_webpage",
    ) -> ManusTask:
        """
        创建动画任务
        
        Args:
            chapter: 章节号
            title: 动画标题
            content: 动画内容
            animation_type: 动画类型
        
        Returns:
            ManusTask
        """
        prompt = f"""请创建一个关于{title}的交互式动画演示。

内容：
{content}

技术要求：
- 使用 React 和 Tailwind CSS 构建前端界面
- 使用 CSS 动画和过渡效果实现平滑的视觉体验
- 提供交互式探索功能
- 部署到 Manus 平台

输出格式：
- 完整的 React 代码
- 可公开访问的演示链接"""
        
        return self.create_task(
            title=f"第{chapter}章 {title}",
            content=prompt,
            agent_profile="manus-1.6-max",
        )
    
    def wait_for_task_completion(
        self,
        task_id: str,
        timeout: int = 300,
        poll_interval: int = 5,
    ) -> dict:
        """
        等待任务完成
        
        Args:
            task_id: 任务 ID
            timeout: 超时时间（秒）
            poll_interval: 轮询间隔（秒）
        
        Returns:
            任务结果
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_task_status(task_id)
            
            task_status = status.get("status", "unknown")
            _get_logger().info(f"任务 {task_id} 状态：{task_status}")
            
            if task_status == "completed":
                return status
            elif task_status in ["failed", "stopped"]:
                raise Exception(f"任务 {task_id} 失败：{task_status}")
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"任务 {task_id} 超时")
