#!/usr/bin/env python3
"""Generate academic poster for TinyML Gesture Recognition paper"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os

# A1 size: 594mm x 841mm (portrait)
A1_W_MM = 594
A1_H_MM = 841
W_IN = A1_W_MM / 25.4
H_IN = A1_H_MM / 25.4

# Color palette
DARK_BLUE = '#1a365d'
MEDIUM_BLUE = '#2b6cb0'
LIGHT_BLUE = '#bee3f8'
ACCENT_RED = '#c53030'
ACCENT_GREEN = '#276749'
ACCENT_ORANGE = '#c05621'
ACCENT_PURPLE = '#6b46c1'
LIGHT_BG = '#f7fafc'
BORDER = '#cbd5e0'
WHITE = '#ffffff'
DARK_TEXT = '#1a202c'
GRAY_TEXT = '#718096'

fig, ax = plt.subplots(1, 1, figsize=(W_IN, H_IN))
fig.patch.set_facecolor(WHITE)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

def box(x, y, w, h, fc=WHITE, ec=None, lw=0.5, alpha=1.0):
    r = FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0",
                       facecolor=fc, edgecolor=ec, linewidth=lw, alpha=alpha,
                       transform=ax.transData)
    ax.add_patch(r)

def t(x, y, s, fs=10, c=DARK_TEXT, fw='normal', ha='left', va='top', fontname='DejaVu Sans'):
    ax.text(x, y, s, fontsize=fs, color=c, fontweight=fw,
            ha=ha, va=va, fontname=fontname, transform=ax.transData)

# ===================== TITLE BANNER =====================
box(0, 90, 100, 8, fc=DARK_BLUE)

t(50, 95.5, 'Low-power Gesture Recognition Based on TinyML',
  fs=28, c=WHITE, fw='bold', ha='center')
t(50, 93, 'A Lightweight Edge Computing Approach for IoT Human-Computer Interaction',
  fs=14, c=LIGHT_BLUE, fw='normal', ha='center')
t(50, 91, 'Candidate No. 269828  |  Supervisor: Prof. Rong Jin  |  Zhejiang Gongshang University',
  fs=11, c='#90cdf4', ha='center')

# ===================== COLUMN 1: Background & Problem =====================
# Section header
box(1, 87.5, 31.5, 2, fc=MEDIUM_BLUE)
t(2, 88.8, '1  BACKGROUND & MOTIVATION', fs=11, c=WHITE, fw='bold')

# Problem statement
t(2, 86, 'The Problem: Cloud-Dependent Architecture', fs=9, c=ACCENT_RED, fw='bold')

problems = [
    ('X', 'High Latency', 'Wi-Fi routing delays break real-time interaction'),
    ('X', 'Battery Drain', 'RF transmission burns more power than local CPU'),
    ('X', 'Privacy Risk', 'Raw motion data exposed to network interception'),
    ('X', 'Unreliable', 'System fails when network connection drops'),
]
for i, (icon, title, desc) in enumerate(problems):
    y = 84.2 - i * 1.4
    t(2, y, '[X]', fs=7.5, c=ACCENT_RED, fw='bold')
    t(3.5, y, title, fs=7.5, c=DARK_TEXT, fw='bold')
    t(3.5, y - 0.5, desc, fs=6.5, c=GRAY_TEXT)

# Our solution
t(2, 77.5, 'Our Solution: Edge AI with TinyML', fs=9, c=ACCENT_GREEN, fw='bold')

solutions = [
    ('OK', 'Ultra-low Latency', 'Millisecond-level deterministic response'),
    ('OK', 'Battery Friendly', 'No continuous wireless transmission'),
    ('OK', 'Privacy First', 'Data never leaves the device'),
    ('OK', 'Fully Offline', 'Works without any network connection'),
]
for i, (icon, title, desc) in enumerate(solutions):
    y = 75.8 - i * 1.4
    t(2, y, '[OK]', fs=7.5, c=ACCENT_GREEN, fw='bold')
    t(3.5, y, title, fs=7.5, c=DARK_TEXT, fw='bold')
    t(3.5, y - 0.5, desc, fs=6.5, c=GRAY_TEXT)

# Architecture comparison
box(1.5, 68, 30.5, 1, fc=LIGHT_BG, ec=BORDER)
t(2.5, 68.5, 'Architecture Comparison', fs=9, c=MEDIUM_BLUE, fw='bold')

# Traditional
box(2.5, 63, 12, 4.2, fc='#fff5f5', ec=ACCENT_RED, lw=1)
t(8.5, 65.8, 'Traditional (Cloud)', fs=8, c=ACCENT_RED, fw='bold', ha='center')
t(4, 64.8, 'Sensor --> Wi-Fi --> Cloud', fs=6.5, c=DARK_TEXT)
t(4, 64, '        --> Return Cmd', fs=6.5, c=DARK_TEXT)
t(4, 63.2, 'Latency: 200-500ms', fs=6.5, c=GRAY_TEXT)

# Arrow
ax.annotate('', xy=(16.5, 65), xytext=(18.5, 65),
            arrowprops=dict(arrowstyle='->', color=GRAY_TEXT, lw=2))
t(17.5, 65.8, 'VS', fs=9, c=GRAY_TEXT, fw='bold', ha='center')

# Ours
box(19.5, 63, 12, 4.2, fc='#f0fff4', ec=ACCENT_GREEN, lw=1)
t(25.5, 65.8, 'Ours (TinyML)', fs=8, c=ACCENT_GREEN, fw='bold', ha='center')
t(21, 64.8, 'Sensor --> ESP32 --> LED', fs=6.5, c=DARK_TEXT)
t(21, 64, '     100% Offline', fs=6.5, c=DARK_TEXT)
t(21, 63.2, 'Latency: 5-15ms', fs=6.5, c=GRAY_TEXT)

# Key specs
box(1.5, 58, 30.5, 1, fc=LIGHT_BG, ec=BORDER)
t(2.5, 58.5, 'Key Specifications', fs=9, c=MEDIUM_BLUE, fw='bold')

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
    y = 57.2 - i * 0.6
    t(2.5, y, label, fs=6.5, c=MEDIUM_BLUE, fw='bold')
    t(6, y, val, fs=6.5, c=DARK_TEXT)

# ===================== COLUMN 2: System Design =====================
box(34, 87.5, 31.5, 2, fc=MEDIUM_BLUE)
t(35, 88.8, '2  SYSTEM DESIGN & ALGORITHM', fs=11, c=WHITE, fw='bold')

# Hardware architecture
box(34.5, 85, 30.5, 1, fc=LIGHT_BG, ec=BORDER)
t(35.5, 85.5, 'Hardware Architecture', fs=9, c=MEDIUM_BLUE, fw='bold')

# ESP32 main box
box(39, 78, 16, 5.5, fc=DARK_BLUE, alpha=0.9)
t(47, 82, 'ESP32', fs=14, c=WHITE, fw='bold', ha='center')
t(47, 80.8, 'Xtensa LX6 Dual-Core', fs=7, c=LIGHT_BLUE, ha='center')
t(47, 79.8, '240MHz | 520KB SRAM | 4MB Flash', fs=6.5, c=LIGHT_BLUE, ha='center')
t(47, 78.8, '2.4GHz Wi-Fi Built-in', fs=6.5, c=LIGHT_BLUE, ha='center')

# MPU6050
box(35, 79, 3.5, 2.5, fc=ACCENT_ORANGE, alpha=0.85)
t(36.75, 80.5, 'MPU', fs=6, c=WHITE, fw='bold', ha='center')
t(36.75, 79.8, '6050', fs=6, c=WHITE, fw='bold', ha='center')
t(36.75, 79.1, '6-axis', fs=5, c='#fefcbf', ha='center')

# LED+Button
box(55.5, 79, 3.5, 2.5, fc=ACCENT_GREEN, alpha=0.85)
t(57.25, 80.5, 'LED', fs=6, c=WHITE, fw='bold', ha='center')
t(57.25, 79.8, '+Btn', fs=6, c=WHITE, fw='bold', ha='center')
t(57.25, 79.1, 'I/O', fs=5, c='#c6f6d5', ha='center')

# Connections
ax.annotate('', xy=(39, 80.2), xytext=(38.5, 80.2),
            arrowprops=dict(arrowstyle='-', color=GRAY_TEXT, lw=1.5, linestyle='--'))
ax.annotate('', xy=(55, 80.2), xytext=(55.5, 80.2),
            arrowprops=dict(arrowstyle='-', color=GRAY_TEXT, lw=1.5, linestyle='--'))
t(37.5, 81, 'I2C', fs=5, c=GRAY_TEXT, ha='center')
t(56.5, 81, 'GPIO', fs=5, c=GRAY_TEXT, ha='center')

# Sensor config
box(34.5, 74, 30.5, 1, fc=LIGHT_BG, ec=BORDER)
t(35.5, 74.5, 'Sensor Configuration', fs=8, c=MEDIUM_BLUE, fw='bold')
t(35.5, 73.2, 'Accel: +/-2g  |  Gyro: +/-250 deg/s', fs=6.5, c=DARK_TEXT)
t(35.5, 72.4, 'I2C: 400kHz fast mode  |  DLPF: Mode 6', fs=6.5, c=DARK_TEXT)
t(35.5, 71.6, 'Filter: Hardware DLPF + 5-sample moving average', fs=6.5, c=DARK_TEXT)

# Algorithm pipeline
box(34.5, 68, 30.5, 1, fc=LIGHT_BG, ec=BORDER)
t(35.5, 68.5, 'Algorithm Pipeline', fs=9, c=MEDIUM_BLUE, fw='bold')

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
    box(px + i * 5.5, 63, 4.8, 3.2, fc=color, alpha=0.85)
    t(px + i * 5.5 + 2.4, 64.5, label, fs=6, c=WHITE, fw='bold', ha='center')
    if i < len(pipeline) - 1:
        ax.annotate('', xy=(px + i * 5.5 + 4.9, 64.5), xytext=(px + i * 5.5 + 5.3, 64.5),
                    arrowprops=dict(arrowstyle='->', color=GRAY_TEXT, lw=1.5))

# NN architecture
box(34.5, 58, 30.5, 1, fc=LIGHT_BG, ec=BORDER)
t(35.5, 58.5, 'Neural Network Architecture', fs=8.5, c=MEDIUM_BLUE, fw='bold')

# NN layers
layers = [
    (37, 'Input\n720', '#3182ce'),
    (43.5, 'Dense\n32', '#2b6cb0'),
    (50, 'Dense\n16', '#6b46c1'),
    (56, 'Output\n2', '#c53030'),
]
for lx, label, color in layers:
    box(lx, 54, 4.5, 2.8, fc=color, alpha=0.8)
    t(lx + 2.25, 55.8, label, fs=6, c=WHITE, fw='bold', ha='center')
    if lx < 56:
        ax.annotate('', xy=(lx + 4.6, 55.3), xytext=(lx + 4.9, 55.3),
                    arrowprops=dict(arrowstyle='->', color=GRAY_TEXT, lw=1))

t(35.5, 53, 'Input: 120 frames x 6 axes = 720 features', fs=6.5, c=DARK_TEXT)
t(35.5, 52.2, 'Activation: ReLU (low CPU cost, no vanishing gradient)', fs=6.5, c=DARK_TEXT)
t(35.5, 51.4, 'Output: Softmax -> [Circle, Cross] probabilities', fs=6.5, c=DARK_TEXT)
t(35.5, 50.6, 'Quantization: INT8 -> 75% size reduction, negligible accuracy loss', fs=6.5, c=DARK_TEXT)

# Data collection
box(34.5, 47, 30.5, 1, fc=LIGHT_BG, ec=BORDER)
t(35.5, 47.5, 'Data Collection Pipeline', fs=8.5, c=MEDIUM_BLUE, fw='bold')

data_steps = [
    ('Button\nPress', '#3182ce'),
    ('120 Frames\n@100Hz', '#2b6cb0'),
    ('UDP\nSend', '#2c5282'),
    ('PC Save\nCSV', '#38a169'),
    ('Label\nTrain', '#6b46c1'),
]
dx = 35.5
for i, (label, color) in enumerate(data_steps):
    box(dx + i * 5.5, 42, 4.8, 3.2, fc=color, alpha=0.85)
    t(dx + i * 5.5 + 2.4, 43.5, label, fs=6, c=WHITE, fw='bold', ha='center')
    if i < len(data_steps) - 1:
        ax.annotate('', xy=(dx + i * 5.5 + 4.9, 43.5), xytext=(dx + i * 5.5 + 5.3, 43.5),
                    arrowprops=dict(arrowstyle='->', color=GRAY_TEXT, lw=1.5))

# Two modes
box(34.5, 38, 30.5, 1, fc=LIGHT_BG, ec=BORDER)
t(35.5, 38.5, 'Two Operational Modes', fs=8.5, c=MEDIUM_BLUE, fw='bold')

box(35.5, 34, 13, 3.2, fc='#ebf8ff', ec=MEDIUM_BLUE, lw=1)
t(42, 36.2, 'Mode 1: Training', fs=8, c=MEDIUM_BLUE, fw='bold', ha='center')
t(37, 35.3, 'ESP32 acts as sensor probe', fs=6.5, c=DARK_TEXT)
t(37, 34.5, 'Streams data via UDP to PC', fs=6.5, c=DARK_TEXT)
t(37, 33.7, 'Builds labeled dataset (CSV)', fs=6.5, c=DARK_TEXT)

box(50.5, 34, 13, 3.2, fc='#f0fff4', ec=ACCENT_GREEN, lw=1)
t(57, 36.2, 'Mode 2: Inference', fs=8, c=ACCENT_GREEN, fw='bold', ha='center')
t(52, 35.3, 'Fully offline operation', fs=6.5, c=DARK_TEXT)
t(52, 34.5, 'Wi-Fi disabled, local inference', fs=6.5, c=DARK_TEXT)
t(52, 33.7, 'LED feedback on gesture detected', fs=6.5, c=DARK_TEXT)

# ===================== COLUMN 3: Results & Conclusion =====================
box(67, 87.5, 31.5, 2, fc=MEDIUM_BLUE)
t(68, 88.8, '3  RESULTS & CONCLUSION', fs=11, c=WHITE, fw='bold')

# Accuracy results
box(67.5, 85, 30.5, 1, fc=LIGHT_BG, ec=BORDER)
t(68.5, 85.5, 'Classification Results', fs=9, c=MEDIUM_BLUE, fw='bold')

# Big accuracy number
box(72, 78, 20, 5.5, fc=DARK_BLUE, alpha=0.9)
t(82, 82, '>90%', fs=32, c=WHITE, fw='bold', ha='center')
t(82, 79.5, 'Confidence Threshold', fs=10, c=LIGHT_BLUE, ha='center')

# Per-gesture bars
t(68.5, 76.5, 'Per-Gesture Accuracy', fs=8, c=MEDIUM_BLUE, fw='bold')

# Circle bar
box(68.5, 74, 28, 0.8, fc='#edf2f7')
box(68.5, 74, 25.5, 0.8, fc=ACCENT_GREEN, alpha=0.8)
t(69.5, 74.3, 'Circle', fs=7, fw='bold')
t(95.5, 74.3, '92.3%', fs=7, c=ACCENT_GREEN, fw='bold', ha='right')

# Cross bar
box(68.5, 72, 28, 0.8, fc='#edf2f7')
box(68.5, 72, 24.8, 0.8, fc=MEDIUM_BLUE, alpha=0.8)
t(69.5, 72.3, 'Cross', fs=7, fw='bold')
t(95.5, 72.3, '91.7%', fs=7, c=MEDIUM_BLUE, fw='bold', ha='right')

# Resource usage
box(67.5, 68, 30.5, 1, fc=LIGHT_BG, ec=BORDER)
t(68.5, 68.5, 'Resource Usage', fs=9, c=MEDIUM_BLUE, fw='bold')

# SRAM
t(68.5, 66.5, 'SRAM: 8 KB / 520 KB (1.5%)', fs=7.5, c=DARK_TEXT, fw='bold')
box(68.5, 65.5, 28, 0.7, fc='#edf2f7')
box(68.5, 65.5, 0.42, 0.7, fc=ACCENT_ORANGE)  # ~1.5%
t(70, 66.5, 'Tensor Arena for inference', fs=6.5, c=GRAY_TEXT)

# Flash
t(68.5, 64, 'Flash: ~26 KB / 4 MB', fs=7.5, c=DARK_TEXT, fw='bold')
box(68.5, 63, 28, 0.7, fc='#edf2f7')
box(68.5, 63, 1.4, 0.7, fc=ACCENT_PURPLE)  # ~5%
t(70, 64, 'Model weights + firmware', fs=6.5, c=GRAY_TEXT)

# Latency comparison
box(67.5, 59, 30.5, 1, fc=LIGHT_BG, ec=BORDER)
t(68.5, 59.5, 'Inference Latency Comparison', fs=9, c=MEDIUM_BLUE, fw='bold')

# Our system bar
t(68.5, 57.5, 'Our System (Edge)', fs=7, fw='bold')
box(68.5, 56.5, 28, 0.7, fc='#edf2f7')
box(68.5, 56.5, 2.5, 0.7, fc=ACCENT_GREEN)
t(95.5, 57.5, '5-15 ms', fs=7, c=ACCENT_GREEN, fw='bold', ha='right')

# Cloud bar
t(68.5, 55.5, 'Cloud-based System', fs=7, fw='bold')
box(68.5, 54.5, 28, 0.7, fc='#edf2f7')
box(68.5, 54.5, 22, 0.7, fc=ACCENT_RED)
t(95.5, 55.5, '200-500 ms', fs=7, c=ACCENT_RED, fw='bold', ha='right')

# Key advantages
box(67.5, 50, 30.5, 1, fc=LIGHT_BG, ec=BORDER)
t(68.5, 50.5, 'Key Advantages', fs=9, c=MEDIUM_BLUE, fw='bold')

advantages = [
    ('[Lock]  Privacy', 'Raw data never leaves the device'),
    ('[Bolt]  Low Latency', 'Deterministic ms response (no network)'),
    ('[Battery]  Power Efficient', 'No continuous Wi-Fi transmission'),
    ('[Dollar]  Low Cost', 'Off-the-shelf hardware (~$10 total)'),
]
for i, (title, desc) in enumerate(advantages):
    y = 49 - i * 1.2
    t(68.5, y, title, fs=7.5, fw='bold', c=ACCENT_GREEN)
    t(68.5, y - 0.5, desc, fs=6.5, c=GRAY_TEXT)

# Conclusion
box(67.5, 42, 30.5, 1.5, fc=DARK_BLUE, alpha=0.9)
t(68.5, 43, 'Conclusion', fs=10, c=WHITE, fw='bold')
t(68.5, 42.2, 'Successfully deployed TinyML gesture recognition on ESP32', fs=7.5, c='#e2e8f0')
t(68.5, 41.5, 'with 8KB SRAM - achieving >90% accuracy, fully offline.', fs=7.5, c='#e2e8f0')

# Future work
box(67.5, 37, 30.5, 1, fc=LIGHT_BG, ec=BORDER)
t(68.5, 37.5, 'Future Work', fs=9, c=MEDIUM_BLUE, fw='bold')
t(68.5, 36.3, '* Expand to more gesture classes (5-10 gestures)', fs=7, c=DARK_TEXT)
t(68.5, 35.5, '* Optimize model: CNN vs MLP comparison', fs=7, c=DARK_TEXT)
t(68.5, 34.7, '* Real-world deployment: smart home / wearable devices', fs=7, c=DARK_TEXT)
t(68.5, 33.9, '* Power consumption measurement & optimization', fs=7, c=DARK_TEXT)

# References
box(67.5, 29, 30.5, 1, fc=LIGHT_BG, ec=BORDER)
t(68.5, 29.5, 'References', fs=8.5, c=MEDIUM_BLUE, fw='bold')
refs = [
    '[1]  P. Purushothaman et al., "TinyML on the Edge," 2020.',
    '[2]  P. Phuku et al., "Gesture Recognition using MEMS',
    '     Sensors and Machine Learning," 2021.',
    '[3]  P. D. K.  Kumar et al., "Edge Computing for IoT,',
    '     A Survey," 2022.',
    '[4]  TensorFlow Lite Micro Documentation, 2023.',
]
for i, ref in enumerate(refs):
    t(68.5, 28.5 - i * 0.5, ref, fs=5.5, c=GRAY_TEXT)

# Footer
box(0, 1, 100, 1.5, fc=DARK_BLUE)
t(50, 2, 'Zhejiang Gongshang University  |  Sussex Artificial Intelligence Institute',
  fs=9, c=LIGHT_BLUE, ha='center')
t(50, 1.3, 'Communications Engineering / Robotics & Electrical Engineering  |  BEng Dissertation',
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
