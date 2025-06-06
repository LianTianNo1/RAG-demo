#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端构建脚本

@remarks 自动安装依赖、构建React前端并集成到Python服务器
@author AI Assistant
@version 1.0
"""

import os
import subprocess
import shutil
import sys
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """
    运行命令并打印输出
    
    @param command - 要执行的命令
    @param cwd - 工作目录
    @param check - 是否检查返回码
    @returns 命令执行结果
    """
    print(f"执行命令: {command}")
    if cwd:
        print(f"工作目录: {cwd}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.stdout:
            print("输出:", result.stdout)
        if result.stderr:
            print("错误:", result.stderr)
            
        return result
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if e.stdout:
            print("输出:", e.stdout)
        if e.stderr:
            print("错误:", e.stderr)
        raise

def check_node_npm():
    """
    检查Node.js和npm是否已安装
    
    @returns 如果都已安装返回True，否则返回False
    """
    try:
        # 检查Node.js
        node_result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if node_result.returncode != 0:
            print("❌ Node.js未安装")
            return False
        print(f"✅ Node.js版本: {node_result.stdout.strip()}")
        
        # 检查npm
        npm_result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if npm_result.returncode != 0:
            print("❌ npm未安装")
            return False
        print(f"✅ npm版本: {npm_result.stdout.strip()}")
        
        return True
    except FileNotFoundError:
        print("❌ Node.js或npm未找到，请先安装Node.js")
        print("下载地址: https://nodejs.org/")
        return False

def install_dependencies():
    """
    安装前端依赖
    
    @returns 安装成功返回True，否则返回False
    """
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("❌ frontend目录不存在")
        return False
    
    print("📦 安装前端依赖...")
    try:
        # 使用npm安装依赖
        run_command("npm install", cwd=frontend_dir)
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败")
        return False

def build_frontend():
    """
    构建前端项目
    
    @returns 构建成功返回True，否则返回False
    """
    frontend_dir = Path("frontend")
    
    print("🔨 构建前端项目...")
    try:
        # 构建项目
        run_command("npm run build", cwd=frontend_dir)
        print("✅ 前端构建完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 前端构建失败")
        return False

def integrate_with_python():
    """
    将构建的前端集成到Python服务器
    
    @returns 集成成功返回True，否则返回False
    """
    static_dir = Path("static")
    
    # 检查构建输出是否存在
    if not static_dir.exists():
        print("❌ 构建输出目录不存在")
        return False
    
    print("🔗 集成前端到Python服务器...")
    
    # 更新Python服务器以支持静态文件服务
    server_file = Path("rag_api_server.py")
    if not server_file.exists():
        print("❌ rag_api_server.py文件不存在")
        return False
    
    # 读取服务器文件内容
    with open(server_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经添加了静态文件支持
    if 'StaticFiles' not in content:
        print("📝 添加静态文件支持到服务器...")
        
        # 在导入部分添加StaticFiles
        import_line = "from fastapi.responses import StreamingResponse"
        new_import = "from fastapi.responses import StreamingResponse\nfrom fastapi.staticfiles import StaticFiles"
        content = content.replace(import_line, new_import)
        
        # 在app初始化后添加静态文件挂载
        app_init = 'app.add_middleware('
        static_mount = '''# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware('''
        content = content.replace(app_init, static_mount)
        
        # 添加前端路由
        root_route = '''@app.get("/")
async def root():
    """根端点，返回API信息"""'''
        
        new_root_route = '''@app.get("/app")
async def frontend_app():
    """前端应用入口"""
    from fastapi.responses import FileResponse
    import os
    
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="前端应用未找到")

@app.get("/")
async def root():
    """根端点，返回API信息"""'''
        
        content = content.replace(root_route, new_root_route)
        
        # 写回文件
        with open(server_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 静态文件支持已添加到服务器")
    else:
        print("✅ 服务器已支持静态文件")
    
    return True

def main():
    """
    主函数
    
    @returns 无返回值
    """
    print("🚀 开始构建React前端")
    print("=" * 50)
    
    # 1. 检查Node.js和npm
    print("1️⃣ 检查Node.js环境...")
    if not check_node_npm():
        sys.exit(1)
    print()
    
    # 2. 安装依赖
    print("2️⃣ 安装前端依赖...")
    if not install_dependencies():
        sys.exit(1)
    print()
    
    # 3. 构建前端
    print("3️⃣ 构建前端项目...")
    if not build_frontend():
        sys.exit(1)
    print()
    
    # 4. 集成到Python服务器
    print("4️⃣ 集成到Python服务器...")
    if not integrate_with_python():
        sys.exit(1)
    print()
    
    print("=" * 50)
    print("✅ 前端构建完成！")
    print()
    print("🎯 使用方法:")
    print("1. 启动服务器: python rag_api_server.py")
    print("2. 访问前端: http://localhost:8000/app")
    print("3. API文档: http://localhost:8000/docs")
    print()
    print("📁 文件说明:")
    print("- static/ - 构建后的前端文件")
    print("- frontend/ - React源代码")
    print("- rag_api_server.py - 已更新支持静态文件")

if __name__ == "__main__":
    main()
