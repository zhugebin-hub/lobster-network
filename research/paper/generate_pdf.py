#!/usr/bin/env python3
"""
Generate PDF version of the Time-Arbitrage Scheduling paper
Using fpdf2 for PDF generation
"""

from fpdf import FPDF
from datetime import datetime
import os

class AcademicPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        # Add Unicode support
        self.add_font('DejaVu', '', '/usr/share/fonts/dejavu/DejaVuSans.ttf', uni=True)
        self.add_font('DejaVu', 'B', '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf', uni=True)
        self.add_font('DejaVu', 'I', '/usr/share/fonts/dejavu/DejaVuSans-Oblique.ttf', uni=True)
        
    def header(self):
        # Lightweight header
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 5, 'Time-Arbitrage Scheduling for Heterogeneous Cloud Computing', 0, 1, 'C')
        self.ln(2)
        
    def footer(self):
        self.set_y(-10)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 5, f'Page {self.page_no()}', 0, 0, 'C')

def read_markdown_file(path):
    """Read the markdown paper draft"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def parse_markdown_sections(content):
    """Parse markdown into sections"""
    sections = []
    current_section = {'title': 'Abstract', 'content': []}
    
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip YAML front matter
        if line.startswith('---') and i == 0:
            while i < len(lines) and lines[i] != '---':
                i += 1
            i += 1
            continue
            
        # Section headers
        if line.startswith('## '):
            if current_section['content']:
                sections.append(current_section)
            current_section = {'title': line[3:].strip(), 'content': []}
        elif line.startswith('### '):
            current_section['content'].append(('subsection', line[4:].strip()))
        elif line.startswith('#### '):
            current_section['content'].append(('subsubsection', line[5:].strip()))
        elif line.startswith('- **'):
            # List item with bold
            current_section['content'].append(('list', line))
        elif line.startswith('- '):
            current_section['content'].append(('list', line[2:]))
        elif line.startswith('```'):
            # Code block
            code_lines = [line]
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            code_lines.append(lines[i])
            current_section['content'].append(('code', '\n'.join(code_lines)))
        elif line.startswith('|'):
            # Table - collect all table lines
            table_lines = []
            while i < len(lines) and lines[i].startswith('|'):
                table_lines.append(lines[i])
                i += 1
            i -= 1
            current_section['content'].append(('table', table_lines))
        elif line.startswith('**') and '**:' in line:
            current_section['content'].append(('bold_text', line))
        elif line.strip() and not line.startswith('#'):
            current_section['content'].append(('text', line))
        
        i += 1
    
    if current_section['content']:
        sections.append(current_section)
    
    return sections

def generate_pdf():
    """Generate the PDF paper"""
    
    # Read the markdown content
    md_path = '/home/admin/.openclaw/workspace/research/paper/paper_draft_v1.md'
    content = read_markdown_file(md_path)
    
    # Create PDF
    pdf = AcademicPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font('DejaVu', 'B', 16)
    pdf.multi_cell(0, 8, 'Time-Arbitrage Scheduling for\nHeterogeneous Cloud Computing:\nLearning from Power Grid Dispatch', 0, 'C')
    pdf.ln(10)
    
    # Authors
    pdf.set_font('DejaVu', '', 11)
    pdf.cell(0, 6, 'Bin Zhuge, OpenClaw Research Agent', 0, 1, 'C')
    pdf.cell(0, 6, 'OpenClaw Research Lab, Hangzhou, China', 0, 1, 'C')
    pdf.ln(5)
    
    # Date
    pdf.set_font('DejaVu', 'I', 9)
    pdf.cell(0, 5, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
    pdf.cell(0, 5, 'Target: ICDCS 2026 / HPDC 2026', 0, 1, 'C')
    pdf.ln(10)
    
    # Abstract
    pdf.add_page()
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 6, 'Abstract', 0, 1)
    pdf.set_font('DejaVu', '', 10)
    
    # Find and add abstract from content
    abstract_start = content.find('**Abstract**')
    if abstract_start != -1:
        abstract_text = content[abstract_start + 12:content.find('**Keywords**')]
        abstract_text = abstract_text.replace('**', '').replace('\n', ' ')
        pdf.multi_cell(0, 5, abstract_text.strip())
    pdf.ln(5)
    
    # Keywords
    pdf.set_font('DejaVu', 'I', 10)
    keywords_start = content.find('**Keywords**')
    if keywords_start != -1:
        keywords_end = content.find('\n\n', keywords_start)
        keywords = content[keywords_start + 12:keywords_end].replace('**', '').strip()
        pdf.cell(0, 5, f'Keywords: {keywords}', 0, 1)
    
    # Parse and add sections
    sections = parse_markdown_sections(content)
    
    for section in sections:
        if section['title'] in ['Abstract', 'Keywords', '', 'References']:
            continue
            
        pdf.add_page()
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 8, section['title'], 0, 1)
        pdf.set_font('DejaVu', '', 10)
        
        for item_type, item_content in section['content']:
            if item_type == 'text':
                if item_content.strip():
                    pdf.multi_cell(0, 5, item_content.strip())
            elif item_type == 'subsection':
                pdf.ln(3)
                pdf.set_font('DejaVu', 'B', 11)
                pdf.cell(0, 6, item_content, 0, 1)
                pdf.set_font('DejaVu', '', 10)
            elif item_type == 'subsubsection':
                pdf.ln(2)
                pdf.set_font('DejaVu', 'B', 10)
                pdf.cell(0, 5, item_content, 0, 1)
                pdf.set_font('DejaVu', '', 10)
            elif item_type == 'list':
                text = item_content if isinstance(item_content, str) else str(item_content)
                text = text.replace('**', '').replace('*', '')
                pdf.cell(5)
                pdf.multi_cell(0, 5, f'- {text}', 0, 1)
            elif item_type == 'bold_text':
                text = item_content.replace('**', '')
                pdf.multi_cell(0, 5, text)
            elif item_type == 'code':
                pdf.set_font('DejaVu', '', 8)
                pdf.set_fill_color(240, 240, 240)
                code_text = item_content.replace('```python', '').replace('```yaml', '').replace('```', '')
                pdf.multi_cell(0, 4, code_text, 0, 1, fill=True)
                pdf.set_font('DejaVu', '', 10)
            elif item_type == 'table':
                # Simple table rendering
                for row in item_content[:5]:  # Limit rows
                    row_text = row.replace('|', ' | ').strip()
                    pdf.set_font('DejaVu', '', 8)
                    pdf.cell(0, 4, row_text, 0, 1)
                pdf.set_font('DejaVu', '', 10)
    
    # Add references section
    pdf.add_page()
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 8, 'References', 0, 1)
    pdf.set_font('DejaVu', '', 9)
    
    # Extract references from content
    ref_start = content.find('## References')
    if ref_start != -1:
        ref_content = content[ref_start + 13:]
        for line in ref_content.split('\n')[:30]:  # Limit references
            if line.startswith('['):
                pdf.multi_cell(0, 4, line.strip())
    
    # Add appendix
    pdf.add_page()
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 8, 'Appendix A: Reproducibility', 0, 1)
    pdf.set_font('DejaVu', '', 10)
    
    appendix_text = """
Simulation Parameters and configuration details for reproducibility.

Resources:
- CPU: 6 × 32 cores @ $0.05/hour
- GPU: 4 × 8 units (A100) @ $3.50/hour
- NPU: 3 × 16 units (Ascend) @ $2.00/hour
- Memory: 2 × 256 GB @ $0.01/hour

Workload:
- Realtime: 20%, 30s SLA
- Inference: 30%, 120s SLA
- Training: 20%, 2h SLA
- Batch: 30%, 4h SLA

Price Model:
- High: 10:00-16:00, 20:00-23:00 (3× base)
- Medium: 6:00-9:00, 17:00-19:00 (1.5× base)
- Low: otherwise (1× base)

Simulation:
- Duration: 12 hours
- Repetitions: 3
- Time step: 60 seconds
"""
    pdf.multi_cell(0, 5, appendix_text.strip())
    
    # Save PDF
    output_path = '/home/admin/.openclaw/workspace/research/paper/paper_v1.pdf'
    pdf.output(output_path)
    
    print(f"PDF generated successfully: {output_path}")
    print(f"File size: {os.path.getsize(output_path) / 1024:.1f} KB")
    return output_path

if __name__ == '__main__':
    generate_pdf()
