#!/usr/bin/env python3
"""
使用 Playwright 渲染 Mermaid 流程图为 PNG
"""
from playwright.sync_api import sync_playwright
import os

workspace = "/home/admin/.openclaw/workspace"
mmd_path = os.path.join(workspace, "esp32-audio-flowchart.mmd")
output_path = os.path.join(workspace, "esp32-audio-flowchart.png")

# 读取 mermaid 文件
with open(mmd_path, 'r') as f:
    mermaid_code = f.read()

# 创建 HTML 模板
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ margin: 0; padding: 20px; background: #ffffff; }}
    </style>
</head>
<body>
    <div class="mermaid">
{mermaid_code}
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'default',
            flowchart: {{ useMaxWidth: false, htmlLabels: true }}
        }});
    </script>
</body>
</html>
"""

temp_html = os.path.join(workspace, "temp_flowchart.html")
with open(temp_html, 'w') as f:
    f.write(html_content)

print(f"临时 HTML 已创建：{temp_html}")

try:
    with sync_playwright() as p:
        print("启动浏览器...")
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = browser.new_page()
        
        print(f"加载页面：file://{temp_html}")
        page.goto(f"file://{temp_html}")
        
        print("等待 mermaid 渲染...")
        page.wait_for_selector(".mermaid svg", timeout=15000)
        page.wait_for_timeout(3000)
        
        print(f"截图保存到：{output_path}")
        page.screenshot(path=output_path, full_page=True)
        
        browser.close()
        print(f"✅ 流程图已生成：{output_path}")
        
except Exception as e:
    print(f"❌ 错误：{e}")
    raise
