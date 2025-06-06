@echo off
chcp 65001 >nul
echo 🚀 构建React前端
echo ==========================================

echo 1️⃣ 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js未安装，请先安装Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm未安装
    pause
    exit /b 1
)

echo ✅ Node.js环境正常
echo.

echo 2️⃣ 进入前端目录...
cd frontend
if errorlevel 1 (
    echo ❌ frontend目录不存在
    pause
    exit /b 1
)

echo 3️⃣ 安装依赖...
npm install
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo 4️⃣ 构建项目...
npm run build
if errorlevel 1 (
    echo ❌ 构建失败
    pause
    exit /b 1
)

cd ..

echo.
echo ==========================================
echo ✅ 前端构建完成！
echo.
echo 🎯 使用方法:
echo 1. 启动服务器: python rag_api_server.py
echo 2. 访问前端: http://localhost:8000/app
echo 3. API文档: http://localhost:8000/docs
echo.
pause
