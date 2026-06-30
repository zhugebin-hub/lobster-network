#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import os

workspace = "/home/admin/.openclaw/workspace"
html_path = os.path.join(workspace, "flowchart.html")
output_path = os.path.join(workspace, "esp32-audio-flowchart.png")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # 加载 HTML 文件
    page.goto(f"file://{html_path}")
    
    # 等待 mermaid 渲染完成
    page.wait_for_selector(".mermaid svg", timeout=10000)
    
    # 等待一下确保完全渲染
    page.wait_for_timeout(2000)
    
    # 截图
    page.screenshot(path=output_path, full_page=True)
    
    browser.close()
    print(f"流程图已生成：{output_path}")
