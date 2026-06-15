#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Combine fig_01.png to fig_10.png into a single composite image"""

from PIL import Image
import os

output_dir = '/home/admin/.openclaw/workspace/调查数据图形'
output_path = os.path.join(output_dir, 'fig_01-10_combined.png')

# Load images
images = []
for i in range(1, 11):
    fn = os.path.join(output_dir, f'fig_{i:02d}.png')
    images.append(Image.open(fn))

# Determine layout: 2 columns x 5 rows
# Find max width per column (col 0: images 0,2,4,6,8; col 1: images 1,3,5,7,9)
col0_width = max(images[i].size[0] for i in [0, 2, 4, 6, 8])
col1_width = max(images[i].size[0] for i in [1, 3, 5, 7, 9])

# Normalize heights for each row
row_heights = []
for row in range(5):
    idx_a = row * 2
    idx_b = row * 2 + 1
    h_a = images[idx_a].size[1]
    h_b = images[idx_b].size[1]
    row_heights.append(max(h_a, h_b))

# Add padding between images
pad_x = 40
pad_y = 30
border = 50

total_width = col0_width + col1_width + pad_x + border * 2
total_height = sum(row_heights) + pad_y * 4 + border * 2

# Create composite
composite = Image.new('RGB', (total_width, total_height), 'white')

for row in range(5):
    idx_a = row * 2
    idx_b = row * 2 + 1
    img_a = images[idx_a]
    img_b = images[idx_b]
    
    # Resize to match column widths while maintaining aspect ratio
    # Resize to fit column width, scale height proportionally
    new_h_a = int(img_a.size[1] * (col0_width / img_a.size[0]))
    img_a_resized = img_a.resize((col0_width, new_h_a), Image.LANCZOS)
    
    new_h_b = int(img_b.size[1] * (col1_width / img_b.size[0]))
    img_b_resized = img_b.resize((col1_width, new_h_b), Image.LANCZOS)
    
    # Center vertically in row
    y_offset = border + sum(row_heights[:row]) + pad_y * row
    row_h = row_heights[row]
    
    # Paste img_a
    x_a = border
    y_a = y_offset + (row_h - img_a_resized.size[1]) // 2
    composite.paste(img_a_resized, (x_a, y_a))
    
    # Paste img_b
    x_b = border + col0_width + pad_x
    y_b = y_offset + (row_h - img_b_resized.size[1]) // 2
    composite.paste(img_b_resized, (x_b, y_b))

# Save with high quality
composite.save(output_path, dpi=(200, 200), quality=95)
print(f'Saved: {output_path}')
print(f'Size: {composite.size}')
