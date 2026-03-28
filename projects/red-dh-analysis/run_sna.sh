#!/bin/bash
# 红楼梦社会网络分析 - 一键运行脚本

set -e

echo "============================================================"
echo "📊 《红楼梦》社会网络分析 - 一键运行"
echo "============================================================"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate

# 检查依赖
echo "🔧 检查依赖..."
pip install -q -r requirements.txt

# 检查数据
if [ ! -f "data/hongloumeng.txt" ]; then
    echo "📖 下载红楼梦文本..."
    mkdir -p data
    curl -s -o data/hongloumeng.txt "https://www.gutenberg.org/files/24260/24260-0.txt"
    echo "✓ 下载完成"
fi

# 运行分析
echo ""
echo "============================================================"
echo "📈 步骤 1/3: 提取人物关系"
echo "============================================================"
python scripts/cooccurrence.py

echo ""
echo "============================================================"
echo "🔬 步骤 2/3: 社会网络分析"
echo "============================================================"
python scripts/sna_analysis.py

echo ""
echo "============================================================"
echo "📊 步骤 3/3: 生成可视化"
echo "============================================================"
python scripts/sna_visualization.py

echo ""
echo "============================================================"
echo "✅ 分析完成！"
echo "============================================================"
echo ""
echo "📁 输出文件:"
echo "  📄 output/sna_full_report.md - 完整分析报告"
echo "  📊 output/sna_results.json - 原始数据"
echo "  📷 output/sna_*.png - 可视化图表"
echo ""
echo "📖 查看报告:"
echo "  cat output/sna_full_report.md"
echo ""
echo "🖼️ 查看图表:"
echo "  open output/sna_network_overview.png  # macOS"
echo "  xdg-open output/sna_network_overview.png  # Linux"
echo ""
