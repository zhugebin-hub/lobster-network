#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉聊天记录导出 - 附件整理脚本

功能：
1. 清理不相关的图片
2. 重命名文件（格式：模块 X_描述_序号。扩展名）
3. 建立标准文件夹结构
4. 生成附件清单 JSON
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

def organize_attachments(case_number, case_name, input_images, output_files, output_dir):
    """
    整理附件
    
    参数：
    - case_number: 案例编号（如 001）
    - case_name: 案例名称
    - input_images: 输入图片列表（字典，包含路径和对应模块）
    - output_files: 产出文件列表
    - output_dir: 输出目录
    """
    
    # 创建目录结构
    os.makedirs(f"{output_dir}/02_产出物", exist_ok=True)
    os.makedirs(f"{output_dir}/03_输入材料", exist_ok=True)
    
    attachment_list = []
    
    # 处理输入图片
    print(f"📸 处理 {len(input_images)} 张输入图片...")
    for img_info in input_images:
        src_path = img_info['path']
        module = img_info['module']
        description = img_info['description']
        index = img_info.get('index', 1)
        
        # 获取文件扩展名
        file_ext = Path(src_path).suffix
        
        # 生成新文件名
        new_filename = f"模块{module}_{description}_{index}{file_ext}"
        dst_path = f"{output_dir}/03_输入材料/{new_filename}"
        
        # 复制文件
        shutil.copy2(src_path, dst_path)
        print(f"  ✅ {new_filename}")
        
        # 添加到清单
        attachment_list.append({
            'name': new_filename,
            'type': '图片',
            'module': f"模块{module}",
            'path': dst_path
        })
    
    # 处理产出文件
    print(f"\n📁 处理 {len(output_files)} 个产出文件...")
    for file_info in output_files:
        src_path = file_info['path']
        category = file_info.get('category', '产出物')
        
        # 复制到产出物目录
        filename = Path(src_path).name
        dst_path = f"{output_dir}/02_产出物/{filename}"
        
        shutil.copy2(src_path, dst_path)
        print(f"  ✅ {filename}")
        
        # 添加到清单
        attachment_list.append({
            'name': filename,
            'type': '文档' if filename.endswith('.docx') else '压缩包',
            'module': category,
            'path': dst_path
        })
    
    # 生成附件清单 JSON
    manifest_path = f"{output_dir}/附件清单.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump({
            'case_number': case_number,
            'case_name': case_name,
            'created_at': datetime.now().isoformat(),
            'attachments': attachment_list
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 附件整理完成！")
    print(f"📦 输出目录：{output_dir}")
    print(f"📄 附件清单：{manifest_path}")
    
    return attachment_list


def cleanup_unrelated_files(output_dir, keep_files):
    """
    清理不相关的文件
    
    参数：
    - output_dir: 输出目录
    - keep_files: 保留的文件列表
    """
    
    input_dir = f"{output_dir}/03_输入材料"
    
    if not os.path.exists(input_dir):
        return
    
    # 获取所有文件
    all_files = os.listdir(input_dir)
    
    # 删除不在保留列表中的文件
    for filename in all_files:
        if filename not in keep_files and not filename.startswith('模块'):
            file_path = os.path.join(input_dir, filename)
            os.remove(file_path)
            print(f"🗑️  已删除：{filename}")


def rename_files(output_dir, rename_map):
    """
    重命名文件
    
    参数：
    - output_dir: 输出目录
    - rename_map: 重命名映射 {旧文件名：新文件名}
    """
    
    input_dir = f"{output_dir}/03_输入材料"
    
    for old_name, new_name in rename_map.items():
        old_path = os.path.join(input_dir, old_name)
        new_path = os.path.join(input_dir, new_name)
        
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            print(f"✏️  重命名：{old_name} → {new_name}")


if __name__ == "__main__":
    # 示例用法
    case_number = "001"
    case_name = "人机协作设计数字人文课程"
    
    input_images = [
        {
            'path': '/home/admin/.openclaw/media/inbound/008ede12-260a-4299-b93d-0a5bc9bbf3df.jpg',
            'module': '1',
            'description': '樱花照片',
            'index': 1
        },
        {
            'path': '/home/admin/.openclaw/media/inbound/c427548e-3663-463b-99a5-a6b072da1a48.jpg',
            'module': '1',
            'description': '樱花照片',
            'index': 2
        }
    ]
    
    output_files = [
        {
            'path': '/home/admin/.openclaw/workspace/digital_humanities_11weeks.docx',
            'category': '模块 5'
        },
        {
            'path': '/home/admin/.openclaw/workspace/week5_package_word.zip',
            'category': '模块 6'
        }
    ]
    
    output_dir = f"/home/admin/.openclaw/workspace/teaching_cases/{case_number}_{case_name}"
    
    organize_attachments(case_number, case_name, input_images, output_files, output_dir)
