#!/usr/bin/env python3
"""Create video with burned-in subtitles using PIL and ffmpeg."""

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = "/home/admin/.openclaw/workspace/video-project/electrical-safety"
WIDTH, HEIGHT = 1920, 1080

# Parse VTT subtitles
def parse_vtt(vtt_file):
    with open(vtt_file, 'r') as f:
        content = f.read()
    
    blocks = content.strip().split('\n\n')
    subtitles = []
    for block in blocks[1:]:  # Skip WEBVTT header
        lines = block.strip().split('\n')
        if len(lines) >= 2:
            time_range = lines[1]
            text = ' '.join(lines[2:])
            start = time_range.split(' --> ')[0].strip()
            end = time_range.split(' --> ')[1].strip()
            # Convert to seconds - handle both comma and dot for milliseconds
            start = start.replace(',', '.')
            end = end.replace(',', '.')
            start_parts = start.split(':')
            end_parts = end.split(':')
            start_sec = float(start_parts[0]) * 3600 + float(start_parts[1]) * 60 + float(start_parts[2])
            end_sec = float(end_parts[0]) * 3600 + float(end_parts[1]) * 60 + float(end_parts[2])
            subtitles.append((start_sec, end_sec, text))
    return subtitles

# Get font
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 36)
except:
    try:
        font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 36)
    except:
        font = ImageFont.load_default()

# Parse subtitles
subs = parse_vtt(os.path.join(OUT_DIR, "subtitles.vtt"))
print(f"Found {len(subs)} subtitle entries")

# Create subtitle frames directory
sub_frames_dir = os.path.join(OUT_DIR, "sub_frames")
os.makedirs(sub_frames_dir, exist_ok=True)

# Create a black background for subtitle frames
bg = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))

# Generate subtitle frames at 30fps
fps = 30
max_duration = max(end for _, end, _ in subs) + 1
total_frames = int(max_duration * fps)

print(f"Generating {total_frames} subtitle frames...")

for frame_idx in range(total_frames):
    time_sec = frame_idx / fps
    
    # Find active subtitle
    active_text = ""
    for start, end, text in subs:
        if start <= time_sec <= end:
            active_text = text
            break
    
    if active_text:
        # Create subtitle overlay
        img = bg.copy()
        draw = ImageDraw.Draw(img)
        
        # Calculate text position (bottom center)
        bbox = draw.textbbox((0, 0), active_text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (WIDTH - text_w) // 2
        y = HEIGHT - 120
        
        # Draw text background
        padding = 10
        draw.rectangle(
            [x - padding, y - padding, x + text_w + padding, y + text_h + padding],
            fill=(0, 0, 0, 180)
        )
        
        # Draw text
        draw.text((x, y), active_text, fill=(255, 255, 255, 255), font=font)
        
        # Save frame
        frame_file = os.path.join(sub_frames_dir, f"sub_{frame_idx:06d}.png")
        img.save(frame_file)
    else:
        # Create empty frame (transparent)
        frame_file = os.path.join(sub_frames_dir, f"sub_{frame_idx:06d}.png")
        bg.save(frame_file)
    
    if frame_idx % 100 == 0:
        print(f"  Generated {frame_idx}/{total_frames} frames")

print("Subtitle frames generated!")
print(f"Total frames: {total_frames}")
