#!/usr/bin/env python3
# 生成自包含 HTML 脚本（图片内嵌 base64）
# 用法：python3 generate_html.py <content.html> <images_dir> <output.html>

import re
import sys
import os
import base64
from PIL import Image
import io

def generate_html(content_path, images_dir, output_path, quality=60, max_dim=800):
    """生成自包含 HTML（图片内嵌 base64）"""
    
    # 读取内容
    with open(content_path, 'r', encoding='utf-8') as f:
        content_div = f.read()
    
    # 提取所有图片
    images = re.findall(r'data-src="([^"]+)"', content_div)
    print(f"找到 {len(images)} 张图片")
    
    # 压缩并内嵌图片
    for i, img_url in enumerate(images):
        img_path = os.path.join(images_dir, f'img_{i:02d}.jpg')
        if os.path.exists(img_path):
            try:
                # 打开并转换
                img = Image.open(img_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 调整尺寸
                if max(img.size) > max_dim:
                    ratio = max_dim / max(img.size)
                    new_size = tuple(int(d * ratio) for d in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # 压缩保存
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=quality)
                img_data = base64.b64encode(buffer.getvalue()).decode()
                data_uri = f'data:image/jpeg;base64,{img_data}'
                
                # 替换
                old = f'data-src="{img_url}"'
                new = f'src="{data_uri}"'
                content_div = content_div.replace(old, new)
                print(f"  压缩 img_{i:02d}.jpg ({len(img_data)//1024} KB)")
            except Exception as e:
                print(f"  处理失败 img_{i}: {e}")
    
    # 清理属性
    content_div = re.sub(r'\s*style="[^"]*"', '', content_div)
    content_div = re.sub(r'\s*data-[^=]+="[^"]*"', '', content_div)
    content_div = re.sub(r'\s*class="[^"]*"', '', content_div)
    
    # 构建完整 HTML
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>微信公众号文章</title>
<style>
  body {{
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "WenQuanYi Micro Hei", sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 40px 20px;
    line-height: 1.8;
    color: #333;
    font-size: 16px;
  }}
  h1 {{
    font-size: 24px;
    text-align: center;
    margin-bottom: 10px;
    color: #1a1a1a;
  }}
  .meta {{
    text-align: center;
    color: #888;
    font-size: 14px;
    margin-bottom: 40px;
    border-bottom: 1px solid #eee;
    padding-bottom: 20px;
  }}
  img {{
    max-width: 100%;
    height: auto;
    margin: 20px 0;
    display: block;
  }}
  p {{
    margin: 12px 0;
    text-indent: 2em;
  }}
  section {{
    margin: 20px 0;
  }}
</style>
</head>
<body>
{content_div}
</body>
</html>"""
    
    # 保存
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"HTML 已生成：{os.path.getsize(output_path)/1024:.0f} KB")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("用法：python3 generate_html.py <content.html> <images_dir> <output.html>")
        sys.exit(1)
    
    content_path = sys.argv[1]
    images_dir = sys.argv[2]
    output_path = sys.argv[3]
    
    generate_html(content_path, images_dir, output_path)
