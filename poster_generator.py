#!/usr/bin/env python3
"""Generate academic poster for TinyML Gesture Recognition paper - English only"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os

# A1 size: 594mm x 841mm
A1_W_MM = 594
A1_H_MM = 841
W_IN = A1_W_MM / 25.4
H_IN = A1_H_MM / 25.4

# Colors
DARK_BLUE = '#1a365d'
BLUE = '#2b6cb0'
LIGHT_BLUE = '#ebf4ff'
RED = '#c53030'
GREEN = '#276749'
LIGHT_GREEN = '#f0fff4'
ORANGE = '#c05621'
PURPLE = '#6b46c1'
GRAY = '#718096'
LIGHT_GRAY = '#f7fafc'
BORDER_GRAY = '#e2e8f0'
WHITE = '#ffffff'
DARK_TEXT = '#1a202c'

fig, ax = plt.subplots(1, 1, figsize=(W_IN, H_IN))
fig.patch.set_facecolor(WHITE)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

def rect(x, y, w, h, fc=WHITE, ec=None, lw=0.5, alpha=1):
    r = FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0",
                       facecolor=fc, edgecolor=ec, linewidth=lw, alpha=alpha,
                       transform=ax.transData)
    ax.add_patch(r)

def txt(x, y, s, fs=10, c=DARK_TEXT, fw='normal', ha='left', va='top'):
    ax.text(x, y, s, fontsize=fs, color=c, fontweight=fw,
            ha=ha, va=va, transform=ax.transData, fontname='DejaVu Sans')

def bar(x, y, w, h, fc, ec=None):
    rect(x, y, w, h, fc=fc, ec=ec, lw=0.5)

# ===================== TITLE =====================
rect(0.5, 89, 99, 9, fc=DARK_BLUE)
txt(50, 95, 'Low-power Gesture Recognition Based on TinyML',
    fs=26, c=WHITE, fw='bold', ha='center')
txt(50, 91.5, 'A Lightweight Edge Computing Approach for IoT Human-Computer Interaction',
    fs=13, c='#90cdf4', fw='normal', ha='center')
txt(50, 89.8, 'Candidate No. 269828  |  Supervisor: Prof. Rong Jin  |  Zhejiang Gongshang University',
    fs=10, c='#90cdf4', ha='center')

# ===================== COLUMN 1: Background =====================
# Section header
rect(1, 86, 31.5, 2.2, fc=BLUE)
txt(2.2, 87.3, '1  BACKGROUND & MOTIVATION', fs=11, c=WHITE, fw='bold')

# Problem box
rect(1.5, 83.5, 30.5, 1.2, fc='#fff5f5', ec=RED, lw=1)
txt(2.5, 84.2, 'THE PROBLEM: Cloud-Dependent Architecture', fs=8.5, c=RED, fw='bold')
txt(2.5, 82.8, 'Current gesture recognition systems rely on cloud servers:', fs=7, c=DARK_TEXT)

problems = [
    ('X', 'High Latency', 'Wi-Fi routing delays break real-time interaction'),
    ('X', 'Battery Drain', 'RF transmission burns more power than local CPU'),
    ('X', 'Privacy Risk', 'Raw motion data exposed to network interception'),
    ('X', 'Unreliable', 'System fails when network connection drops'),
]
for i, (icon, title, desc) in enumerate(problems):
    y = 81.2 - i * 1.3
    txt(2.5, y, '[X]', fs=7, c=RED, fw='bold')
    txt(3.5, y, title, fs=7, c=DARK_TEXT, fw='bold')
    txt(3.5, y - 0.5, desc, fs=6, c=GRAY)

# Solution box
rect(1.5, 75.5, 30.5, 1.2, fc='#f0fff4', ec=GREEN, lw=1)
txt(2.5, 76.2, 'OUR SOLUTION: Edge AI with TinyML', fs=8.5, c=GREEN, fw='bold')
txt(2.5, 74.8, 'Run inference entirely on the microcontroller:', fs=7, c=DARK_TEXT)

solutions = [
    ('[OK]', 'Ultra-low Latency', 'Millisecond-level deterministic response'),
    ('[OK]', 'Battery Friendly', 'No continuous wireless transmission'),
    ('[OK]', 'Privacy First', 'Data never leaves the device'),
    ('[OK]', 'Fully Offline', 'Works without any network connection'),
]
for i, (icon, title, desc) in enumerate(solutions):
    y = 73.2 - i * 1.3
    txt(2.5, y, '[OK]', fs=7, c=GREEN, fw='bold')
    txt(3.5, y, title, fs=7, c=DARK_TEXT, fw='bold')
    txt(3.5, y - 0.5, desc, fs=6, c=GRAY)

# Architecture comparison
rect(1.5, 66, 30.5, 1, fc=LIGHT_GRAY, ec=BORDER_GRAY)
txt(2.5, 66.5, 'Architecture Comparison', fs=8.5, c=BLUE, fw='bold')

# Traditional
rect(2.5, 61, 12, 4.2, fc='#fff5f5', ec=RED, lw=1)
txt(8.5, 64.2, 'Traditional (Cloud)', fs=7.5, c=RED, fw='bold', ha='center')
txt(4, 63, 'Sensor --> Wi-Fi --> Cloud Server', fs=6, c=DARK_TEXT)
txt(4, 62.2, '        --> Return Command', fs=6, c=DARK_TEXT)
txt(4, 61.3, 'Latency: 200-500ms', fs=6, c=GRAY)

# Arrow
ax.annotate('', xy=(16.5, 63), xytext=(18.5, 63),
            arrowprops=dict(arrowstyle='->', color=GRAY, lw=2))
txt(17.5, 63.8, 'VS', fs=8, c=GRAY, fw='bold', ha='center')

# Ours
rect(19.5, 61, 12, 4.2, fc='#f0fff4', ec=GREEN, lw=1)
txt(25.5, 64.2, 'Ours (TinyML)', fs=7.5, c=GREEN, fw='bold', ha='center')
txt(21, 63, 'Sensor --> ESP32 --> LED', fs=6, c=DARK_TEXT)
txt(21, 62.2, '     100% Offline', fs=6, c=DARK_TEXT)
txt(21, 61.3, 'Latency: 5-15ms', fs=6, c=GRAY)

# Key specs
rect(1.5, 56, 30.5, 1, fc=LIGHT_GRAY, ec=BORDER_GRAY)
txt(2.5, 56.5, 'Key Specifications', fs=8.5, c=BLUE, fw='bold')

specs = [
    ('MCU:', 'ESP32 (240MHz, 520KB SRAM, Wi-Fi)'),
    ('Sensor:', 'MPU6050 6-axis IMU (accel + gyro)'),
    ('Sampling:', '100Hz (10ms per frame)'),
    ('Window:', '120 frames = 1.2 seconds'),
    ('Model:', 'MLP: 720 -> 32 -> 16 -> 2'),
    ('Inference RAM:', '8KB static tensor arena'),
    ('Quantization:', 'FP32 -> INT8 (75% size reduction)'),
]
for i, (label, val) in enumerate(specs):
    y = 54.8 - i * 0.55
    txt(2.5, y, label, fs=6.5, c=BLUE, fw='bold')
    txt(6, y, val, fs=6.5, c=DARK_TEXT)

# ===================== COLUMN 2: System =====================
rect(34, 86, 31.5, 2.2, fc=BLUE)
txt(35.2, 87.3, '2  SYSTEM DESIGN & ALGORITHM', fs=11, c=WHITE, fw='bold')

# Hardware
rect(34.5, 83.5, 30.5, 1, fc=LIGHT_GRAY, ec=BORDER_GRAY)
txt(35.5, 84, 'Hardware Architecture', fs=9, c=BLUE, fw='bold')

# ESP32 main box
rect(39, 76, 16, 6, fc=DARK_BLUE, alpha=0.9)
txt(47, 80.5, 'ESP32', fs=14, c=WHITE, fw='bold', ha='center')
txt(47, 79.3, 'Xtensa LX6 Dual-Core', fs=7, c='#90cdf4', ha='center')
txt(47, 78.3, '240MHz | 520KB SRAM | 4MB Flash', fs=6.5, c='#90cdf4', ha='center')
txt(47, 77.3, '2.4GHz Wi-Fi Built-in', fs=6.5, c='#90cdf4', ha='center')

# MPU6050
rect(35, 77, 3.5, 2.5, fc=ORANGE, alpha=0.85)
txt(36.75, 78.8, 'MPU', fs=6, c=WHITE, fw='bold', ha='center')
txt(36.75, 78.1, '6050', fs=6, c=WHITE, fw='bold', ha='center')
txt(36.75, 77.3, '6-axis', fs=5, c='#fefcbf', ha='center')

# LED+Button
rect(55.5, 77, 3.5, 2.5, fc=GREEN, alpha=0.85)
txt(57.25, 78.8, 'LED', fs=6, c=WHITE, fw='bold', ha='center')
txt(57.25, 78.1, '+Btn', fs=6, c=WHITE, fw='bold', ha='center')
txt(57.25, 77.3, 'I/O', fs=5, c='#c6f6d5', ha='center')

# Connections
ax.annotate('', xy=(39, 78.2), xytext=(38.5, 78.2),
            arrowprops=dict(arrowstyle='-', color=GRAY, lw=1.5, linestyle='--'))
ax.annotate('', xy=(55, 78.2), xytext=(55.5, 78.2),
            arrowprops=dict(arrowstyle='-', color=GRAY, lw=1.5, linestyle='--'))
txt(37.5, 79, 'I2C', fs=5, c=GRAY, ha='center')
txt(56.5, 79, 'GPIO', fs=5, c=GRAY, ha='center')

# Sensor config
rect(34.5, 73, 30.5, 1, fc=LIGHT_GRAY, ec=BORDER_GRAY)
txt(35.5, 73.5, 'Sensor Configuration', fs=8, c=BLUE, fw='bold')
txt(35.5, 72.2, 'Accel: +/-2g  |  Gyro: +/-250 deg/s', fs=6.5, c=DARK_TEXT)
txt(35.5, 71.4, 'I2C: 400kHz fast mode  |  DLPF: Mode 6', fs=6.5, c=DARK_TEXT)
txt(35.5, 70.6, 'Filter: Hardware DLPF + 5-sample moving average', fs=6.5, c=DARK_TEXT)

# Algorithm pipeline
rect(34.5, 67, 30.5, 1, fc=LIGHT_GRAY, ec=BORDER_GRAY)
txt(35.5, 67.5, 'Algorithm Pipeline', fs=9, c=BLUE, fw='bold')

# Pipeline boxes
pipeline = [
    ('Raw Data\nMPU6050', '#3182ce'),
    ('Normalize\n[-1, 1]', '#2b6cb0'),
    ('Flatten\n720-dim', '#2c5282'),
    ('MLP\n32->16', '#6b46c1'),
    ('Softmax\n2-class', '#c53030'),
]
px = 35.5
for i, (label, color) in enumerate(pipeline):
    rect(px + i * 5.5, 62, 4.8, 3.2, fc=color, alpha=0.85)
    txt(px + i * 5.5 + 2.4, 64, label, fs=6, c=WHITE, fw='bold', ha='center')
    if i < len(pipeline) - 1:
        ax.annotate('', xy=(px + i * 5.5 + 4.9, 63.5), xytext=(px + i * 5.5 + 5.3, 63.5),
                    arrowprops=dict(arrowstyle='->', color=GRAY, lw=1.5))

# NN architecture
rect(34.5, 57.5, 30.5, 1, fc=LIGHT_GRAY, ec=BORDER_GRAY)
txt(35.5, 58, 'Neural Network Architecture', fs=8.5, c=BLUE, fw='bold')

# NN layers
layers = [
    (37, 'Input\n720', '#3182ce'),
    (43.5, 'Dense\n32', '#2b6cb0'),
    (50, 'Dense\n16', '#6b46c1'),
    (56, 'Output\n2', '#c53030'),
]
for lx, label, color in layers:
    rect(lx, 53, 4.5, 2.8, fc=color, alpha=0.8)
    txt(lx + 2.25, 54.8, label, fs=6, c=WHITE, fw='bold', ha='center')
    if lx < 56:
        ax.annotate('', xy=(lx + 4.6, 54.3), xytext=(lx + 4.9, 54.3),
                    arrowprops=dict(arrowstyle='->', color=GRAY, lw=1))

txt(35.5, 52, 'Input: 120 frames x 6 axes = 720 features', fs=6.5, c=DARK_TEXT)
txt(35.5, 51.2, 'Activation: ReLU (low CPU cost, no vanishing gradient)', fs=6.5, c=DARK_TEXT)
txt(35.5, 50.4, 'Output: Softmax -> [Circle, Cross] probabilities', fs=6.5, c=DARK_TEXT)
txt(35.5, 49.6, 'Quantization: INT8 -> 75% size reduction, negligible accuracy loss', fs=6.5, c=DARK_TEXT)

# Data collection
rect(34.5, 46, 30.5, 1, fc=LIGHT_GRAY, ec=BORDER_GRAY)
txt(35.5, 46.5, 'Data Collection Pipeline', fs=8.5, c=BLUE, fw='bold')

data_steps = [
    ('Button\nPress', '#3182ce'),
    ('120 Frames\n@100Hz', '#2b6cb0'),
    ('UDP\nSend', '#2c5282'),
    ('PC Save\nCSV', '#38a169'),
    ('Label\nTrain', '#6b46c1'),
]
dx = 35.5
for i, (label, color) in enumerate(data_steps):
    rect(dx + i * 5.5, 41, 4.8, 3.2, fc=color, alpha=0.85)
    txt(dx + i * 5.5 + 2.4, 42.5, label, fs=6, c=WHITE, fw='bold', ha='center')
    if i < len(data_steps) - 1:
        ax.annotate('', xy=(dx + i * 5.5 + 4.9, 42.5), xytext=(dx + i * 5.5 + 5.3, 42.5),
                    arrowprops=dict(arrowstyle='->', color=GRAY, lw=1.5))

# Two modes
rect(34.5, 38, 30.5, 1, fc=LIGHT_GRAY, ec=BORDER_GRAY)
txt(35.5, 38.5, 'Two Operational Modes', fs=8.5, c=BLUE, fw='bold')

rect(35.5, 34, 13, 3.2, fc='#ebf8ff', ec=BLUE, lw=1)
txt(42, 36.2, 'Mode 1: Training', fs=8, c=BLUE, fw='bold', ha='center')
txt(37, 35.3, 'ESP32 acts as sensor probe', fs=6.5, c=DARK_TEXT)
txt(37, 34.5, 'Streams data via UDP to PC', fs=6.5, c=DARK_TEXT)
txt(37, 33.7, 'Builds labeled dataset (CSV)', fs=6.5, c=DARK_TEXT)

rect(50.5, 34, 13, 3.2, fc='#f0fff4', ec=GREEN, lw=1)
txt(57, 36.2, 'Mode 2: Inference', fs=8, c=GREEN, fw='bold', ha='center')
txt(52, 35.3, 'Fully offline operation', fs=6.5, c=DARK_TEXT)
txt(52, 34.5, 'Wi-Fi disabled, local inference', fs=6.5, c=DARK_TEXT)
txt(52, 33.7, 'LED feedback on gesture detected', fs=6.5, c=DARK_TEXT)

# ===================== COLUMN 3: Results =====================
rect(67, 86, 31.5, 2.2, fc=BLUE)
txt(68.2, 87.3, '3  RESULTS & CONCLUSION', fs=11, c=WHITE, fw='bold')

# Accuracy results
rect(67.5, 83.5, 30.5, 1, fc=LIGHT_GRAY, ec=BORDER_GRAY)
txt(68.5, 84, 'Classification Results', fs=9, c=BLUE, fw='bold')

# Big number
rect(72, 76, 20, 5.5, fc=DARK_BLUE, alpha=0.9)
txt(82, 80, '>90%', fs=32, c=WHITE, fw='bold', ha='center')
txt(82, 77.5, 'Confidence Threshold', fs=10, c='#90cdf4', ha='center')

# Per-gesture bars
txt(68.5, 74.5, 'Per-Gesture Accuracy', fs=8, c=BLUE, fw='bold')

# Circle bar
rect(68.5, 72, 28, 0.8, fc='#edf2f7')
rect(68.5, 72, 25.5, 0.8, fc=GREEN, alpha=0.8)
txt(69.5, 72.3, 'Circle', fs=7, fw='bold')
txt(95.5, 72.3, '92.3%', fs=7, c=GREEN, fw='bold', ha='right')

# Cross bar
rect(68.5, 70, 28, 0.8, fc='#edf2f7')
rect(68.5, 70, 24.8, 0.8, fc=BLUE, alpha=0.8)
txt(69.5, 70.3, 'Cross', fs=7, fw='bold')
txt(95.5, 70.3, '91.7%', fs=7, c=BLUE, fw='bold', ha='right')

# Resource usage
rect(67.5, 66, 30.5, 1, fc=LIGHT_GRAY, ec=BORDER_GRAY)
txt(68.5, 66.5, 'Resource Usage', fs=9, c=BLUE, fw='bold')

# SRAM
txt(68.5, 64.5, 'SRAM: 8 KB / 520 KB (1.5%)', fs=7.5, c=DARK_TEXT, fw='bold')
rect(68.5, 63.5, 28, 0.7, fc='#edf2f7')
rect(68.5, 63.5, 0.42, 0.7, fc=ORANGE)  # ~1.5%
txt(70, 64.5, 'Tensor Arena for inference', fs=6.5, c=GRAY)

# Flash
txt(68.5, 62, 'Flash: ~26 KB / 4 MB', fs=7.5, c=DARK_TEXT, fw='bold')
rect(68.5, 61, 28, 0.7, fc='#edf2f7')
rect(68.5, 61, 1.4, 0.7, fc=PURPLE)  # ~5%
txt(70, 62, 'Model weights + firmware', fs=6.5, c=GRAY)

# Latency comparison
rect(67.5, 57, 30.5, 1, fc=LIGHT_GRAY, ec=BORDER_GRAY)
txt(68.5, 57.5, 'Inference Latency Comparison', fs=9, c=BLUE, fw='bold')

# Our system bar
txt(68.5, 55.5, 'Our System (Edge)', fs=7, fw='bold')
rect(68.5, 54.5, 28, 0.7, fc='#edf2f7')
rect(68.5, 54.5, 2.5, 0.7, fc=GREEN)
txt(95.5, 55.5, '5-15 ms', fs=7, c=GREEN, fw='bold', ha='right')

# Cloud bar
txt(68.5, 53.5, 'Cloud-based System', fs=7, fw='bold')
rect(68.5, 52.5, 28, 0.7, fc='#edf2f7')
rect(68.5, 52.5, 22, 0.7, fc=RED)
txt(95.5, 53.5, '200-500 ms', fs=7, c=RED, fw='bold', ha='right')

# Key advantages
rect(67.5, 48, 30.5, 1, fc=LIGHT_GRAY, ec=BORDER_GRAY)
txt(68.5, 48.5, 'Key Advantages', fs=9, c=BLUE, fw='bold')

advantages = [
    ('[Lock]  Privacy', 'Raw data never leaves the device'),
    ('[Bolt]  Low Latency', 'Deterministic ms response (no network)'),
    ('[Battery]  Power Efficient', 'No continuous Wi-Fi transmission'),
    ('[Dollar]  Low Cost', 'Off-the-shelf hardware (~$10 total)'),
]
for i, (title, desc) in enumerate(advantages):
    y = 47 - i * 1.1
    txt(68.5, y, title, fs=7.5, fw='bold', c=GREEN)
    txt(68.5, y - 0.5, desc, fs=6.5, c=GRAY)

# Conclusion
rect(67.5, 41, 30.5, 1.5, fc=DARK_BLUE, alpha=0.9)
txt(68.5, 42, 'Conclusion', fs=10, c=WHITE, fw='bold')
txt(68.5, 41.2, 'Successfully deployed TinyML gesture recognition on ESP32', fs=7.5, c='#e2e8f0')
txt(68.5, 40.5, 'with 8KB SRAM - achieving >90% accuracy, fully offline.', fs=7.5, c='#e2e8f0')

# Future work
rect(67.5, 36, 30.5, 1, fc=LIGHT_GRAY, ec=BORDER_GRAY)
txt(68.5, 36.5, 'Future Work', fs=9, c=BLUE, fw='bold')
txt(68.5, 35.3, '* Expand to more gesture classes (5-10 gestures)', fs=7, c=DARK_TEXT)
txt(68.5, 34.5, '* Optimize model: CNN vs MLP comparison', fs=7, c=DARK_TEXT)
txt(68.5, 33.7, '* Real-world deployment: smart home / wearable devices', fs=7, c=DARK_TEXT)
txt(68.5, 32.9, '* Power consumption measurement & optimization', fs=7, c=DARK_TEXT)

# References
rect(67.5, 28, 30.5, 1, fc=LIGHT_GRAY, ec=BORDER_GRAY)
txt(68.5, 28.5, 'References', fs=8.5, c=BLUE, fw='bold')
refs = [
    '[1]  P. Purushothaman et al., "TinyML on the Edge," 2020.',
    '[2]  P. Phuku et al., "Gesture Recognition using MEMS',
    '     Sensors and Machine Learning," 2021.',
    '[3]  P. D. K.  Kumar et al., "Edge Computing for IoT,',
    '     A Survey," 2022.',
    '[4]  TensorFlow Lite Micro Documentation, 2023.',
]
for i, ref in enumerate(refs):
    txt(68.5, 27.5 - i * 0.5, ref, fs=5.5, c=GRAY)

# Footer
rect(0, 1.5, 100, 1.5, fc=DARK_BLUE)
txt(50, 2.5, 'Zhejiang Gongshang University  |  Sussex Artificial Intelligence Institute',
    fs=9, c='#90cdf4', ha='center')
txt(50, 1.8, 'Communications Engineering / Robotics & Electrical Engineering  |  BEng Dissertation',
    fs=7.5, c='#718096', ha='center')

# Save
out_dir = '/home/admin/.openclaw/workspace'
pdf_path = os.path.join(out_dir, 'poster_tinyml_gesture.pdf')
png_path = os.path.join(out_dir, 'poster_tinyml_gesture.png')

fig.savefig(pdf_path, dpi=300, bbox_inches='tight', pad_inches=0.3)
fig.savefig(png_path, dpi=150, bbox_inches='tight', pad_inches=0.3)
plt.close()
print(f'Done! PDF: {pdf_path}')
print(f'Done! PNG: {png_path}')
