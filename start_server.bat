@echo off
chcp 65001 >nul
echo 🚀 启动RAG Excel API服务器...
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或不在PATH中
    echo 请先安装Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python环境正常
echo.

echo 正在启动服务器...
echo 📍 服务地址: http://localhost:8000
echo 📖 API文档: http://localhost:8000/docs
echo 🌐 Web界面: http://localhost:8000/web_demo.html
echo.
echo 按 Ctrl+C 停止服务器
echo ==========================================

python start_server.py

pause
