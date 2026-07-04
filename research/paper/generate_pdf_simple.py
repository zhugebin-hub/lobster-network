#!/usr/bin/env python3
"""
Simple PDF generator for the Time-Arbitrage Scheduling paper
"""

from fpdf import FPDF
from datetime import datetime
import os

class SimplePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        # Add Unicode font
        self.add_font('DejaVu', '', '/usr/share/fonts/dejavu/DejaVuSans.ttf', uni=True)
        self.add_font('DejaVu', 'B', '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf', uni=True)
        self.add_font('DejaVu', 'I', '/usr/share/fonts/dejavu/DejaVuSans-Oblique.ttf', uni=True)

def generate_pdf():
    pdf = SimplePDF()
    pdf.add_page()
    
    # Title
    pdf.set_font('DejaVu', 'B', 14)
    pdf.multi_cell(0, 7, 'Time-Arbitrage Scheduling for Heterogeneous Cloud Computing:\nLearning from Power Grid Dispatch', 0, 'C')
    pdf.ln(5)
    
    # Authors
    pdf.set_font('DejaVu', '', 10)
    pdf.cell(0, 5, 'Bin Zhuge, OpenClaw Research Agent', 0, 1, 'C')
    pdf.cell(0, 5, 'OpenClaw Research Lab, Hangzhou, China', 0, 1, 'C')
    pdf.ln(3)
    
    # Date
    pdf.set_font('DejaVu', 'I', 9)
    pdf.cell(0, 4, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
    pdf.cell(0, 4, 'Target: ICDCS 2026 / HPDC 2026', 0, 1, 'C')
    pdf.ln(5)
    
    # Read markdown content
    with open('/home/admin/.openclaw/workspace/research/paper/paper_draft_v1.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract abstract
    pdf.add_page()
    pdf.set_font('DejaVu', 'B', 11)
    pdf.cell(0, 6, 'Abstract', 0, 1)
    pdf.set_font('DejaVu', '', 10)
    
    abstract_start = content.find('**Abstract**')
    if abstract_start != -1:
        abstract_end = content.find('**Keywords**')
        abstract = content[abstract_start+12:abstract_end].replace('**', '').replace('\n', ' ').strip()
        # Clean up special characters
        abstract = abstract.replace('—', '-').replace('–', '-').replace('•', '-')
        pdf.multi_cell(0, 5, abstract[:2000])
    pdf.ln(3)
    
    # Keywords
    pdf.set_font('DejaVu', 'I', 10)
    keywords_start = content.find('**Keywords**')
    if keywords_start != -1:
        keywords_end = content.find('\n\n', keywords_start)
        keywords = content[keywords_start+12:keywords_end].replace('**', '').strip()
        pdf.cell(0, 4, f'Keywords: {keywords}', 0, 1)
    
    # Main content - sections
    lines = content.split('\n')
    current_section = None
    in_code_block = False
    code_lines = []
    
    for line in lines:
        # Skip abstract and keywords
        if '**Abstract**' in line or '**Keywords**' in line:
            continue
        
        # Section headers
        if line.startswith('## ') and not line.startswith('###'):
            if current_section and current_section not in ['Abstract', 'Keywords', 'References']:
                pdf.add_page()
            current_section = line[3:].strip()
            pdf.set_font('DejaVu', 'B', 11)
            pdf.cell(0, 6, current_section, 0, 1)
            pdf.set_font('DejaVu', '', 10)
            continue
        
        # Subsections
        if line.startswith('### '):
            pdf.ln(2)
            pdf.set_font('DejaVu', 'B', 10)
            subsection = line[4:].strip()
            pdf.cell(0, 5, subsection, 0, 1)
            pdf.set_font('DejaVu', '', 10)
            continue
        
        # Skip if in references or appendix for brevity
        if current_section in ['References', 'Appendix A: Reproducibility']:
            continue
        
        # Code blocks
        if line.startswith('```'):
            in_code_block = not in_code_block
            if not in_code_block and code_lines:
                pdf.set_font('DejaVu', '', 8)
                pdf.set_fill_color(245, 245, 245)
                code_text = '\n'.join(code_lines[:15])  # Limit code lines
                code_text = code_text.replace('python', '').replace('yaml', '').replace('python3', '')
                pdf.multi_cell(0, 3.5, code_text[:1500], 0, 1, fill=True)
                code_lines = []
                pdf.set_font('DejaVu', '', 10)
            continue
        
        if in_code_block:
            code_lines.append(line)
            continue
        
        # Skip tables for simplicity
        if line.startswith('|'):
            continue
        
        # Regular text
        if line.strip() and not line.startswith('#'):
            # Clean up special characters
            clean_line = line.replace('—', '-').replace('–', '-').replace('•', '-').replace('**', '').replace('$', '')
            clean_line = clean_line.replace('\\', '').replace('_', '')
            if len(clean_line) > 0:
                pdf.multi_cell(0, 5, clean_line[:200])
    
    # Add a summary page
    pdf.add_page()
    pdf.set_font('DejaVu', 'B', 11)
    pdf.cell(0, 6, 'Key Results Summary', 0, 1)
    pdf.set_font('DejaVu', '', 10)
    pdf.ln(3)
    
    summary = """
- Cost Reduction: 92.8% ($3.59 -> $0.26 per 12h)
- Task Completion Rate: 100%
- Average Latency: 156s (same as baseline)
- SLA Violations: 36% (primarily for Realtime tasks)

Economic Impact:
- Medium deployment ($10k/month): Annual savings $111,360
- Large deployment (100x GPU): Annual savings $3.3M+

Contributions:
1. First formal analogy between power grid dispatch and cloud scheduling
2. Multi-level temporal hierarchy (seconds to days)
3. Deadline-aware deferral algorithm
4. Comprehensive evaluation with strong results
"""
    pdf.multi_cell(0, 5, summary.strip())
    
    # Save PDF
    output_path = '/home/admin/.openclaw/workspace/research/paper/paper_v1.pdf'
    pdf.output(output_path)
    
    print(f"PDF generated: {output_path}")
    print(f"File size: {os.path.getsize(output_path) / 1024:.1f} KB")
    return output_path

if __name__ == '__main__':
    generate_pdf()
