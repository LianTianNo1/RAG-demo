#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端环境设置脚本

@remarks 检查环境、创建前端项目结构、安装依赖
@author AI Assistant
@version 1.0
"""

import os
import subprocess
import sys
from pathlib import Path

def check_node_npm():
    """检查Node.js和npm环境"""
    try:
        # 检查Node.js
        node_result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if node_result.returncode != 0:
            print("❌ Node.js未安装")
            print("请访问 https://nodejs.org/ 下载安装Node.js")
            return False
        
        node_version = node_result.stdout.strip()
        print(f"✅ Node.js版本: {node_version}")
        
        # 检查版本是否满足要求 (v16+)
        version_num = int(node_version.replace('v', '').split('.')[0])
        if version_num < 16:
            print(f"⚠️ Node.js版本过低，建议使用v16或更高版本")
        
        # 检查npm
        npm_result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if npm_result.returncode != 0:
            print("❌ npm未安装")
            return False
        
        npm_version = npm_result.stdout.strip()
        print(f"✅ npm版本: {npm_version}")
        
        return True
        
    except FileNotFoundError:
        print("❌ Node.js或npm未找到")
        print("请访问 https://nodejs.org/ 下载安装Node.js")
        return False

def create_frontend_structure():
    """创建前端项目结构"""
    print("📁 检查前端项目结构...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ frontend目录不存在")
        print("请确保所有前端文件已正确创建")
        return False
    
    required_files = [
        "package.json",
        "vite.config.js", 
        "index.html",
        "src/main.jsx",
        "src/App.jsx",
        "src/index.css"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = frontend_dir / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少以下文件:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ 前端项目结构完整")
    return True

def install_dependencies():
    """安装前端依赖"""
    frontend_dir = Path("frontend")
    
    print("📦 安装前端依赖...")
    print("这可能需要几分钟时间，请耐心等待...")
    
    try:
        # 使用npm install安装依赖
        result = subprocess.run(
            ['npm', 'install'],
            cwd=frontend_dir,
            check=True,
            capture_output=True,
            text=True
        )
        
        print("✅ 依赖安装完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ 依赖安装失败")
        print(f"错误信息: {e.stderr}")
        
        # 尝试清理并重新安装
        print("🔄 尝试清理并重新安装...")
        try:
            # 删除node_modules和package-lock.json
            node_modules = frontend_dir / "node_modules"
            package_lock = frontend_dir / "package-lock.json"
            
            if node_modules.exists():
                import shutil
                shutil.rmtree(node_modules)
                print("   已删除node_modules")
            
            if package_lock.exists():
                package_lock.unlink()
                print("   已删除package-lock.json")
            
            # 重新安装
            subprocess.run(
                ['npm', 'install'],
                cwd=frontend_dir,
                check=True,
                capture_output=True,
                text=True
            )
            
            print("✅ 重新安装成功")
            return True
            
        except Exception as retry_error:
            print(f"❌ 重新安装也失败了: {retry_error}")
            return False

def test_build():
    """测试构建"""
    frontend_dir = Path("frontend")
    
    print("🔨 测试构建...")
    try:
        result = subprocess.run(
            ['npm', 'run', 'build'],
            cwd=frontend_dir,
            check=True,
            capture_output=True,
            text=True
        )
        
        # 检查构建输出
        static_dir = Path("static")
        if static_dir.exists() and (static_dir / "index.html").exists():
            print("✅ 构建测试成功")
            return True
        else:
            print("❌ 构建输出不完整")
            return False
            
    except subprocess.CalledProcessError as e:
        print("❌ 构建测试失败")
        print(f"错误信息: {e.stderr}")
        return False

def main():
    """主函数"""
    print("🚀 RAG Excel API - 前端环境设置")
    print("=" * 50)
    
    # 1. 检查Node.js环境
    print("1️⃣ 检查Node.js环境...")
    if not check_node_npm():
        sys.exit(1)
    print()
    
    # 2. 检查项目结构
    print("2️⃣ 检查项目结构...")
    if not create_frontend_structure():
        sys.exit(1)
    print()
    
    # 3. 安装依赖
    print("3️⃣ 安装依赖...")
    if not install_dependencies():
        print("\n💡 如果安装失败，可以尝试:")
        print("   1. 检查网络连接")
        print("   2. 使用国内镜像: npm config set registry https://registry.npmmirror.com")
        print("   3. 手动进入frontend目录执行: npm install")
        sys.exit(1)
    print()
    
    # 4. 测试构建
    print("4️⃣ 测试构建...")
    if not test_build():
        print("\n💡 如果构建失败，请检查:")
        print("   1. 所有依赖是否正确安装")
        print("   2. 源代码是否有语法错误")
        print("   3. 尝试手动构建: cd frontend && npm run build")
        sys.exit(1)
    print()
    
    print("=" * 50)
    print("✅ 前端环境设置完成！")
    print()
    print("🎯 下一步:")
    print("1. 启动后端服务: python rag_api_server.py")
    print("2. 访问前端应用: http://localhost:8000/app")
    print("3. 查看API文档: http://localhost:8000/docs")
    print()
    print("🛠️ 开发模式:")
    print("1. 进入前端目录: cd frontend")
    print("2. 启动开发服务器: npm run dev")
    print("3. 访问开发服务器: http://localhost:3000")
    print()
    print("📝 重新构建:")
    print("   python build_frontend.py")

if __name__ == "__main__":
    main()
