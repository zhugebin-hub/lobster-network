# -*- coding: utf-8 -*-
"""
Gantt Chart for H1043Z Individual Project
Student: Zouqi Chen (269877)
Project: Vision-based Hand Gesture Control of a Robotic Arm
Supervisor: Prof. Yanpei Huang
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

# Set style
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 150

# Task data extracted from logbook
# Format: (Task Name, Start Date, End Date, Phase)
tasks = [
    # Phase 1: Project Initiation
    ("Project Topic Discussion", "2025-06-16", "2025-06-29", "Initiation"),
    ("Final Topic Determination", "2025-06-30", "2025-07-13", "Initiation"),
    
    # Phase 2: Literature Review
    ("Literature Review - Sensor Technology", "2025-07-14", "2025-07-27", "Literature"),
    ("Literature Review - Gesture Recognition", "2025-07-28", "2025-08-10", "Literature"),
    ("Literature Review - Search Strategy", "2025-08-11", "2025-08-24", "Literature"),
    ("Literature Review - Classification Methods", "2025-08-25", "2025-09-21", "Literature"),
    
    # Phase 3: Hardware Procurement
    ("Leap Motion Purchase", "2025-09-22", "2025-10-20", "Hardware"),
    ("Hardware Setup & Environment", "2025-10-21", "2025-11-02", "Hardware"),
    
    # Phase 4: Software Development
    ("Code Analysis (GitHub)", "2025-11-03", "2025-11-16", "Software"),
    ("Mid-term Report Writing", "2025-11-17", "2025-11-30", "Documentation"),
    ("Interim Report - Literature Review", "2025-12-01", "2025-12-14", "Documentation"),
    ("Finger Motion Threshold Program", "2025-12-15", "2026-01-11", "Software"),
    
    # Phase 5: Robotic Arm Integration
    ("Robotic Arm Preparation", "2026-01-12", "2026-01-18", "Integration"),
    ("Environment Debugging (VMware)", "2026-01-19", "2026-01-25", "Integration"),
    ("Servo Installation & Testing", "2026-01-26", "2026-02-08", "Integration"),
    ("Hardware Communication Redesign", "2026-02-09", "2026-02-22", "Integration"),
    ("Python Environment Setup", "2026-02-23", "2026-03-04", "Integration"),
    ("Servo Port Testing (COM3)", "2026-03-05", "2026-03-06", "Integration"),
    ("Servo Write/Read Debugging", "2026-03-07", "2026-03-08", "Integration"),
    
    # Phase 6: System Integration
    ("Matlab-Python Integration Design", "2026-03-09", "2026-03-13", "Integration"),
    ("start.bat Development", "2026-03-14", "2026-03-14", "Integration"),
    ("Gripper & Wrist Function", "2026-03-14", "2026-03-14", "Integration"),
    
    # Phase 7: Testing & Validation
    ("Initial Experiment (Grasping)", "2026-03-14", "2026-03-14", "Testing"),
    ("Multi-participant Testing", "2026-03-15", "2026-03-22", "Testing"),
    
    # Phase 8: Documentation
    ("Dissertation Writing", "2026-03-23", "2026-04-15", "Documentation"),
    ("Final Revision & Submission", "2026-04-16", "2026-04-20", "Documentation"),
]

# Convert date strings to datetime objects
def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")

# Create figure and axis
fig, ax = plt.subplots(figsize=(16, 12))

# Color mapping for phases
phase_colors = {
    "Initiation": "#4CAF50",
    "Literature": "#2196F3",
    "Hardware": "#FF9800",
    "Software": "#9C27B0",
    "Integration": "#F44336",
    "Testing": "#00BCD4",
    "Documentation": "#795548",
}

# Plot tasks
y_positions = range(len(tasks))
bars = []

for i, (task_name, start, end, phase) in enumerate(tasks):
    start_date = parse_date(start)
    end_date = parse_date(end)
    duration = (end_date - start_date).days + 1
    
    bar = ax.barh(i, duration, left=mdates.date2num(start_date), 
                  height=0.6, color=phase_colors.get(phase, "#808080"),
                  edgecolor='white', linewidth=1, alpha=0.9)
    bars.append(bar)

# Format x-axis (dates)
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_minor_locator(mdates.WeekdayLocator())

# Format y-axis (task names)
ax.set_yticks(y_positions)
ax.set_yticklabels([task[0] for task in tasks], fontsize=9)

# Add grid
ax.grid(True, axis='x', linestyle='--', alpha=0.5)
ax.set_axisbelow(True)

# Labels and title
ax.set_xlabel('Timeline (2025-2026)', fontsize=12, fontweight='bold')
ax.set_ylabel('Tasks', fontsize=12, fontweight='bold')
ax.set_title('H1043Z Individual Project - Gantt Chart\n'
             'Vision-based Hand Gesture Control of a Robotic Arm\n'
             'Student: Zouqi Chen (269877) | Supervisor: Prof. Yanpei Huang | Academic Year 2024-25', 
             fontsize=14, fontweight='bold', pad=20)

# Add legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=color, label=phase) 
                   for phase, color in phase_colors.items()]
ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1), 
          borderaxespad=0, fontsize=9, title='Project Phase', title_fontsize=10)

# Add today line (for reference)
today = datetime.now()
ax.axvline(x=mdates.date2num(today), color='red', linestyle='-', linewidth=2, 
           label=f'Today ({today.strftime("%Y-%m-%d")})', alpha=0.7)

# Tight layout
plt.tight_layout()

# Save as PNG
output_path = '/home/admin/.openclaw/workspace/project-gantt-chart-v2.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')

print(f"Gantt chart saved to: {output_path}")
print(f"Total tasks: {len(tasks)}")
print(f"Project duration: 2025-06-16 to 2026-04-20")
print(f"Total duration: {(parse_date('2026-04-20') - parse_date('2025-06-16')).days + 1} days")
