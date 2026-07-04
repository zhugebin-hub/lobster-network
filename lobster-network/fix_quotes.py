#!/usr/bin/env python3
"""Fix quote issues in the PPT generation script."""
with open('/home/admin/.openclaw/workspace/lobster-network/gen_live_broadcast_full.py', 'r') as f:
    content = f.read()

# Fix Chinese quotes that break Python syntax
replacements = {
    '"内置"小龙虾三部曲"教学框架': '"内置小龙虾三部曲教学框架',
    '"\"智能体\"系列课程"': '"智能体系列课程',
}
for old, new in replacements.items():
    content = content.replace(old, new)

with open('/home/admin/.openclaw/workspace/lobster-network/gen_live_broadcast_full.py', 'w') as f:
    f.write(content)

print("Fixed quotes")
