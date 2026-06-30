#!/bin/bash

# Resume Generator Script
# 小龙虾风格简历生成器

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/../templates"
WORKSPACE_DIR="/home/admin/.openclaw/workspace"

# 默认参数
STYLE="lobster"
INPUT=""
OUTPUT=""
PREVIEW=false

# 显示帮助
show_help() {
    cat << EOF
🦞 小龙虾简历生成器

用法：$0 [选项]

选项:
  -s, --style STYLE     简历风格 (lobster|minimal|tech|academic)
  -i, --input FILE      输入数据文件 (JSON 格式)
  -o, --output FILE     输出文件路径
  -p, --preview         仅生成 HTML 预览
  -h, --help            显示帮助信息

示例:
  $0 -s lobster -i user-data.json -o resume.pdf
  $0 -p -i user-data.json  # 仅预览

EOF
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--style)
            STYLE="$2"
            shift 2
            ;;
        -i|--input)
            INPUT="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        -p|--preview)
            PREVIEW=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "❌ 未知选项：$1"
            show_help
            exit 1
            ;;
    esac
done

# 检查输入文件
if [[ -z "$INPUT" ]]; then
    echo "❌ 请提供输入文件 (-i/--input)"
    show_help
    exit 1
fi

if [[ ! -f "$INPUT" ]]; then
    echo "❌ 输入文件不存在：$INPUT"
    exit 1
fi

# 选择模板
TEMPLATE="$TEMPLATE_DIR/${STYLE}.html"
if [[ ! -f "$TEMPLATE" ]]; then
    echo "❌ 模板不存在：$TEMPLATE"
    echo "可用风格：lobster, minimal, tech, academic"
    exit 1
fi

echo "🦞 开始生成简历..."
echo "   风格：$STYLE"
echo "   模板：$TEMPLATE"
echo "   输入：$INPUT"

# 生成 HTML
if [[ -z "$OUTPUT" ]] || [[ "$OUTPUT" == *.html ]]; then
    HTML_OUTPUT="${OUTPUT:-${INPUT%.json}-${STYLE}.html}"
else
    HTML_OUTPUT="${OUTPUT%.pdf}.html"
fi

echo "   输出：$HTML_OUTPUT"

# 使用 Node.js 处理模板（更可靠的模板引擎）
node -e "
const fs = require('fs');
const template = fs.readFileSync('$TEMPLATE', 'utf8');
const data = JSON.parse(fs.readFileSync('$INPUT', 'utf8'));

// 简单模板替换
let html = template;

// 处理简单变量
html = html.replace(/{{name}}/g, data.name || '');
html = html.replace(/{{badge}}/g, data.badge || '');
html = html.replace(/{{title}}/g, data.title || '');
html = html.replace(/{{summary}}/g, data.summary || '');
html = html.replace(/{{update_date}}/g, new Date().toISOString().slice(0, 7));

// 处理数组变量
if (data.contact_items) {
    const contactHtml = data.contact_items.map(item => '<span>' + item + '</span>').join('');
    html = html.replace(/{{#contact_items}}[\s\S]*?{{\/contact_items}}/, contactHtml);
}

if (data.keywords) {
    const keywordHtml = data.keywords.map(k => '<span class=\"keyword-tag\">' + k + '</span>').join('');
    html = html.replace(/{{#keywords}}[\s\S]*?{{\/keywords}}/, keywordHtml);
}

if (data.skills) {
    const skillsHtml = data.skills.map(s => \`
        <div class=\"skill-card\">
            <div class=\"skill-name\">\${s.name}</div>
            <div class=\"skill-desc\">\${s.desc}</div>
        </div>
    \`).join('');
    html = html.replace(/{{#skills}}[\s\S]*?{{\/skills}}/, skillsHtml);
}

if (data.education) {
    const eduHtml = data.education.map(e => \`
        <div class=\"card\">
            <div class=\"card-header\">
                <span class=\"card-title\">\${e.school}</span>
                <span class=\"card-date\">\${e.degree}</span>
            </div>
            <div class=\"card-subtitle\">\${e.major} · \${e.details}</div>
        </div>
    \`).join('');
    html = html.replace(/{{#education}}[\s\S]*?{{\/education}}/, eduHtml);
}

if (data.experience) {
    const expHtml = data.experience.map(e => \`
        <div class=\"card\">
            <div class=\"card-header\">
                <span class=\"card-title\">\${e.role}</span>
                <span class=\"card-date\">\${e.period}</span>
            </div>
            <div class=\"card-subtitle\">\${e.company}</div>
            <div class=\"card-content\">
                \${e.points.map(p => '<p>' + p + '</p>').join('')}
            </div>
        </div>
    \`).join('');
    html = html.replace(/{{#experience}}[\s\S]*?{{\/experience}}/, expHtml);
}

if (data.awards) {
    const awardHtml = data.awards.map(a => \`
        <div class=\"card\">
            <div class=\"card-header\">
                <span class=\"card-title\">\${a.title}</span>
                <span class=\"card-date\">\${a.date}</span>
            </div>
            <span class=\"award-badge award-\${a.level}\">\${a.badge}</span>
        </div>
    \`).join('');
    html = html.replace(/{{#awards}}[\s\S]*?{{\/awards}}/, awardHtml);
}

if (data.projects) {
    const projHtml = data.projects.map(p => \`
        <div class=\"card\">
            <div class=\"card-header\">
                <span class=\"card-title\">\${p.name}</span>
                <span class=\"card-date\">\${p.period}</span>
            </div>
            <div class=\"card-subtitle\">\${p.role}</div>
            <div class=\"card-content\">
                \${p.points.map(pt => '<p>' + pt + '</p>').join('')}
            </div>
        </div>
    \`).join('');
    html = html.replace(/{{#projects}}[\s\S]*?{{\/projects}}/, projHtml);
}

if (data.highlights) {
    const highlightHtml = data.highlights.map(h => '<p>' + h + '</p>').join('');
    html = html.replace(/{{#highlights}}[\s\S]*?{{\/highlights}}/, highlightHtml);
}

if (data.footer_brand) {
    html = html.replace(/{{#footer_brand}}[\s\S]*?{{\/footer_brand}}/, \`
        <div class=\"zjgsu-brand\">
            <span>🦞</span>
            <span>\${data.footer_brand}</span>
            <span>🦞</span>
        </div>
    \`);
} else {
    html = html.replace(/{{#footer_brand}}[\s\S]*?{{\/footer_brand}}/, '');
}

fs.writeFileSync('$HTML_OUTPUT', html);
console.log('✅ HTML 生成成功：' + '$HTML_OUTPUT');
"

# 如果需要生成 PDF
if [[ "$PREVIEW" == false ]] && [[ -n "$OUTPUT" ]] && [[ "$OUTPUT" == *.pdf ]]; then
    echo "🦞 正在生成 PDF..."
    
    PDF_OUTPUT="$OUTPUT"
    
    # 使用 Chrome 生成 PDF
    google-chrome --headless --disable-gpu \
        --print-to-pdf="$PDF_OUTPUT" \
        --print-to-pdf-no-header \
        --print-to-pdf-no-footer \
        --window-size=1200,1600 \
        "$HTML_OUTPUT" 2>&1
    
    if [[ -f "$PDF_OUTPUT" ]]; then
        SIZE=$(ls -lh "$PDF_OUTPUT" | awk '{print $5}')
        echo "✅ PDF 生成成功：$PDF_OUTPUT ($SIZE)"
    else
        echo "⚠️  PDF 生成失败，请检查 Chrome 是否安装"
    fi
fi

echo "🦞 简历生成完成！"
