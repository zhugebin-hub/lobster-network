@echo off
chcp 65001 >nul
echo ========================================
echo     学校排课系统 - 一键启动
echo ========================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python！
    echo.
    echo 请先安装 Python:
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载并安装 Python 3.8 或更高版本
    echo 3. 安装时务必勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [✓] Python 已安装
python --version
echo.

:: 检查 Flask 是否安装
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 正在安装依赖包 (首次运行需要)...
    echo.
    python -m pip install flask flask-cors
    if %errorlevel% neq 0 (
        echo [错误] 安装依赖失败！
        echo 请手动运行：pip install flask flask-cors
        pause
        exit /b 1
    )
    echo [✓] 依赖包安装完成
    echo.
) else (
    echo [✓] 依赖包已安装
    echo.
)

:: 创建数据目录
if not exist "data" mkdir data

:: 启动服务
echo ========================================
echo     正在启动排课系统...
echo ========================================
echo.
echo 📱 浏览器访问地址:
echo    http://localhost:5000
echo.
echo ⚠️  请勿关闭此窗口！
echo    按 Ctrl+C 可停止服务
echo.
echo ========================================
echo.

python app.py

pause
