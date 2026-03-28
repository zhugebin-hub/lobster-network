#!/usr/bin/env python3
"""
Generate simple chart images for the paper using basic shapes
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_bar_chart(filename, title, data, colors):
    """Create a simple bar chart"""
    width, height = 600, 400
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Title
    try:
        font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", 16)
        title_font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", 14)
    except:
        font = ImageFont.load_default()
        title_font = font
    
    draw.text((width//2 - len(title)*3, 20), title, fill='black', font=title_font)
    
    # Bars
    bar_width = 150
    max_val = max([d[1] for d in data])
    chart_height = 250
    base_y = 300
    
    for i, (label, value) in enumerate(data):
        x = 100 + i * 200
        bar_height = (value / max_val) * chart_height if max_val > 0 else 0
        y = base_y - bar_height
        
        # Draw bar
        draw.rectangle([x, y, x + bar_width, base_y], fill=colors[i % len(colors)])
        
        # Draw label
        draw.text((x + 20, base_y + 10), label, fill='black', font=font)
        
        # Draw value
        draw.text((x + 30, y - 20), f'${value:.2f}' if isinstance(value, float) else str(value), fill='black', font=font)
    
    img.save(filename, 'PNG', dpi=(300, 300))
    print(f"Created: {filename}")

# Figure 1: Cost Comparison
create_bar_chart(
    'figures/fig1_cost_comparison.png',
    'Cost Comparison (12h)',
    [('Round-Robin', 3.59), ('Time-Arbitrage', 0.26)],
    ['#3498db', '#2ecc71']
)

# Figure 2: Completion Rate
create_bar_chart(
    'figures/fig2_completion_rate.png',
    'Task Completion Rate',
    [('Round-Robin', 100), ('Time-Arbitrage', 100)],
    ['#3498db', '#2ecc71']
)

# Create placeholder for other figures
for i in range(3, 9):
    fig_titles = {
        3: 'SLA Violations',
        4: 'Latency Comparison',
        5: 'Price Sensitivity',
        6: 'Deferrable Fraction',
        7: 'Hourly Load Pattern',
        8: 'System Architecture'
    }
    width, height = 600, 400
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans.ttf", 14)
    except:
        font = ImageFont.load_default()
    draw.text((150, 180), f'Figure {i}: {fig_titles[i]}', fill='black', font=font)
    draw.text((100, 210), '(See PDF package for full chart)', fill='gray', font=font)
    img.save(f'figures/fig{i}_placeholder.png', 'PNG', dpi=(300, 300))
    print(f"Created: figures/fig{i}_placeholder.png")

print("\nAll charts generated!")
