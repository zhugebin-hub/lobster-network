"""
domains/assessment/__init__.py — 薄包装层
实际实现位于 src/lobster_network/assessment/
此文件保持向后兼容，新代码请直接导入 assessment 包。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from lobster_network.assessment import *  # noqa: F401, F403
