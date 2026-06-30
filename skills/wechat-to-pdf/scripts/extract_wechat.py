#!/usr/bin/env python3
# 微信公众号文章正文提取脚本
# 用法：python3 extract_wechat.py <raw.html> <output_dir>

import re
import sys
import os
import urllib.request

def extract_wechat_content(raw_html_path, output_dir):
    """提取微信公众号文章正文和图片"""
    
    # 读取原始 HTML
    with open(raw_html_path, 'r', encoding='utf-8') as f:
        raw = f.read()
    
    # 提取 js_content
    match = re.search(r'id="js_content"[^>]*>(.*?)</div>\s*<script', raw, re.DOTALL)
    if not match:
        print("错误：未找到 js_content")
        sys.exit(1)
    
    content_div = match.group(1)
    
    # 提取所有图片
    images = re.findall(r'data-src="([^"]+)"', content_div)
    print(f"找到 {len(images)} 张图片")
    
    # 下载图片
    images_dir = os.path.join(output_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    for i, img_url in enumerate(images):
        if img_url.startswith('//'):
            img_url = 'https:' + img_url
        try:
            filename = f'img_{i:02d}.jpg'
            filepath = os.path.join(images_dir, filename)
            urllib.request.urlretrieve(img_url, filepath)
            size = os.path.getsize(filepath)
            print(f"  下载 {filename} ({size/1024:.1f} KB)")
        except Exception as e:
            print(f"  下载失败 {i}: {e}")
    
    # 保存提取的内容
    content_path = os.path.join(output_dir, 'content.html')
    with open(content_path, 'w', encoding='utf-8') as f:
        f.write(content_div)
    
    print(f"内容已保存到：{content_path}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("用法：python3 extract_wechat.py <raw.html> <output_dir>")
        sys.exit(1)
    
    raw_html_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    extract_wechat_content(raw_html_path, output_dir)
