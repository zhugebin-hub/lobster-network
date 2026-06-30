#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper 语音识别脚本
用法：python3 transcribe.py <音频文件> [--model 模型名] [--language 语言代码] [--output-dir 输出目录]
"""

import whisper
import sys
import json
import os
import argparse
from datetime import datetime

def format_timestamp(seconds):
    """将秒数转换为 SRT 格式的时间戳"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def transcribe(audio_path, model_name="medium", language=None, output_dir=None):
    """
    转录音频文件
    
    Args:
        audio_path: 音频文件路径
        model_name: Whisper 模型名称 (tiny, base, small, medium, large)
        language: 语言代码 (zh, en, ja, ko 等)，None 为自动检测
        output_dir: 输出目录，默认为音频文件所在目录
    
    Returns:
        转录文本
    """
    
    # 检查文件是否存在
    if not os.path.exists(audio_path):
        print(f"❌ 文件不存在：{audio_path}")
        return None
    
    # 获取文件信息
    file_size = os.path.getsize(audio_path) / 1024 / 1024
    print(f"📁 音频文件：{os.path.basename(audio_path)}")
    print(f"📊 文件大小：{file_size:.2f} MB")
    print(f"📍 文件路径：{audio_path}")
    
    # 加载模型
    print(f"\n🤖 加载 {model_name} 模型...")
    try:
        model = whisper.load_model(model_name)
    except Exception as e:
        print(f"❌ 模型加载失败：{e}")
        print("💡 请确保已安装 openai-whisper: pip3 install openai-whisper")
        return None
    
    # 转录配置
    options = {
        'verbose': False,
        'fp16': False,  # CPU 模式下禁用 fp16
    }
    
    if language:
        options['language'] = language
        print(f"🌐 指定语言：{language}")
    else:
        print("🌐 自动检测语言...")
    
    # 开始转录
    print("\n⏳ 开始转录（这可能需要几分钟）...")
    start_time = datetime.now()
    
    try:
        result = model.transcribe(audio_path, **options)
    except Exception as e:
        print(f"❌ 转录失败：{e}")
        return None
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # 输出结果
    print(f"\n✅ 转录完成！耗时：{duration:.1f} 秒")
    
    # 检测到的语言
    detected_language = result.get('language', 'unknown')
    print(f"🌐 检测到的语言：{detected_language}")
    
    # 完整文本
    full_text = result.get('text', '').strip()
    
    print("\n" + "="*60)
    print("📝 转录文本")
    print("="*60)
    print(full_text)
    
    # 分段信息
    segments = result.get('segments', [])
    if segments:
        print("\n" + "="*60)
        print("📋 分句详情（带时间戳）")
        print("="*60)
        for i, seg in enumerate(segments, 1):
            start = format_timestamp(seg['start'])
            end = format_timestamp(seg['end'])
            text = seg['text'].strip()
            print(f"[{i}] {start} --> {end}")
            print(f"    {text}")
            print()
    
    # 保存结果
    if output_dir is None:
        output_dir = os.path.dirname(audio_path) or '.'
    
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    
    # 保存 JSON
    json_path = os.path.join(output_dir, f"{base_name}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON 结果已保存：{json_path}")
    
    # 保存纯文本
    txt_path = os.path.join(output_dir, f"{base_name}.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(full_text)
    print(f"✅ 文本结果已保存：{txt_path}")
    
    # 保存 SRT 字幕
    srt_path = os.path.join(output_dir, f"{base_name}.srt")
    with open(srt_path, 'w', encoding='utf-8') as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{format_timestamp(seg['start'])} --> {format_timestamp(seg['end'])}\n")
            f.write(f"{seg['text'].strip()}\n\n")
    print(f"✅ SRT 字幕已保存：{srt_path}")
    
    return full_text

def main():
    parser = argparse.ArgumentParser(
        description='Whisper 语音识别 - 将音频文件转录为文字',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python3 transcribe.py meeting.mp3
  python3 transcribe.py audio.wav --model large
  python3 transcribe.py recording.m4a --language zh --model medium
  python3 transcribe.py interview.mp3 --output-dir ~/transcripts
        '''
    )
    
    parser.add_argument('audio_file', help='音频文件路径')
    parser.add_argument('--model', '-m', 
                        default='medium',
                        choices=['tiny', 'base', 'small', 'medium', 'large'],
                        help='Whisper 模型（默认：medium）')
    parser.add_argument('--language', '-l',
                        help='语言代码（默认：自动检测）, 如：zh, en, ja, ko')
    parser.add_argument('--output-dir', '-o',
                        help='输出目录（默认：音频文件所在目录）')
    
    args = parser.parse_args()
    
    transcribe(
        args.audio_file,
        model_name=args.model,
        language=args.language,
        output_dir=args.output_dir
    )

if __name__ == '__main__':
    main()
