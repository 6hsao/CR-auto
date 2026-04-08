@echo off
chcp 65001 >nul
title 皇室战争自动对战

echo ========================================
echo    皇室战争自动对战脚本
echo ========================================
echo.

cd /d "%~dp0"

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo 检查依赖包...
pip show pillow >nul 2>&1
if errorlevel 1 (
    echo 正在安装必要依赖...
    pip install pillow numpy pywin32
)

echo.
echo 启动参数说明:
echo   -d: 设备ID (默认: 127.0.0.1:5555)
echo   -w: 窗口名称 (默认: 雷电模拟器)
echo   -m: 最大场次 (默认: 10)
echo   -mode: 战斗模式 1v1 或 2v2 (默认: 1v1)
echo   -s: 策略 aggressive/defensive/random (默认: aggressive)
echo   -v: 详细输出
echo.

python main.py -m %1 -mode %2 -s %3 -v

pause
