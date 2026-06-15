@echo off
chcp 65001 >nul
title 中职信息技术考试系统 - 打包工具

echo ========================================
echo   中职信息技术考试系统 - 打包工具
echo ========================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.6+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [√] Python 已安装
python --version
echo.

:: 检查 PyInstaller 是否安装
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装 PyInstaller...
    pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo [错误] PyInstaller 安装失败，请检查网络连接
        pause
        exit /b 1
    )
    echo [√] PyInstaller 安装成功
) else (
    echo [√] PyInstaller 已安装
)
echo.

:: 清理旧的打包文件
echo [提示] 清理旧的打包文件...
if exist build (
    rmdir /s /q build
)
if exist dist (
    rmdir /s /q dist
)
if exist *.spec (
    del /q *.spec
)
echo [√] 清理完成
echo.

:: 开始打包
echo [提示] 开始打包，请稍候...
echo.

python -m PyInstaller ^
    --name 中职信息技术考试系统 ^
    --windowed ^
    --onefile ^
    --icon=NONE ^
    --add-data "questions.json;." ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=tkinter.messagebox ^
    --hidden-import=tkinter.scrolledtext ^
    main.py

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！请检查错误信息
    pause
    exit /b 1
)

echo.
echo ========================================
echo   打包成功！
echo ========================================
echo.
echo 可执行文件位置：dist\中职信息技术考试系统.exe
echo.

:: 询问是否打开 dist 目录
set /p open_dir="是否打开 dist 目录？(Y/N): "
if /i "%open_dir%"=="Y" (
    start dist
)

echo.
pause
