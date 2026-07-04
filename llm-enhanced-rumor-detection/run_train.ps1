# Windows PowerShell 训练启动脚本
# 自动设置 HuggingFace 镜像，避免网络超时

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LLM-Enhanced Rumor Detection 训练脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 设置 HuggingFace 镜像
Write-Host "[1/3] 设置 HuggingFace 镜像..." -ForegroundColor Yellow
$env:HF_ENDPOINT = "https://hf-mirror.com"
Write-Host "  ✓ HF_ENDPOINT = https://hf-mirror.com" -ForegroundColor Green
Write-Host ""

# 检查 Python 环境
Write-Host "[2/3] 检查 Python 环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python 版本: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python 未安装或不在 PATH 中" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 运行训练
Write-Host "[3/3] 启动训练..." -ForegroundColor Yellow
Write-Host "  提示: 首次运行会下载预训练模型（约 870 MB）" -ForegroundColor Cyan
Write-Host "  如果下载失败，请查看 '网络超时问题解决方案.md'" -ForegroundColor Cyan
Write-Host ""

python train.py

# 检查退出码
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ 训练完成" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "❌ 训练失败（退出码: $LASTEXITCODE）" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能的解决方案:" -ForegroundColor Yellow
    Write-Host "1. 查看上面的错误信息" -ForegroundColor White
    Write-Host "2. 如果是网络超时，查看 '网络超时问题解决方案.md'" -ForegroundColor White
    Write-Host "3. 运行测试脚本验证: python test_model_loading.py" -ForegroundColor White
    Write-Host "4. 或运行离线测试: python test_offline.py" -ForegroundColor White
}
