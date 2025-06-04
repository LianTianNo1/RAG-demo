#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG API服务器启动脚本

@remarks 用于启动RAG API服务器，包含环境检查和配置验证
@author AI Assistant
@version 1.0
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """
    检查必要的依赖是否已安装

    @returns 如果所有依赖都已安装返回True，否则返回False
    """
    # 包名映射：安装名 -> 导入名
    package_mapping = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "pandas": "pandas",
        "openpyxl": "openpyxl",
        "sentence-transformers": "sentence_transformers",
        "faiss-cpu": "faiss",  # 关键修复：faiss-cpu包导入时使用faiss
        "langchain": "langchain",
        "langchain-community": "langchain_community",
        "langchain-text-splitters": "langchain_text_splitters",
        "ollama": "ollama",
        "python-multipart": "multipart",  # python-multipart导入时使用multipart
        "watchdog": "watchdog"
    }

    missing_packages = []

    for install_name, import_name in package_mapping.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(install_name)

    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n请运行以下命令安装依赖:")
        print("pip install " + " ".join(missing_packages))
        print("或者运行: install_dependencies.bat (Windows) 或 bash install_dependencies.sh (Linux/macOS)")
        return False

    print("✅ 所有依赖包已安装")
    return True

def check_ollama():
    """
    检查Ollama服务是否可用

    @returns 如果Ollama可用返回True，否则返回False
    """
    try:
        import ollama
        # 尝试连接Ollama
        client = ollama.Client()
        models = client.list()
        print(f"✅ Ollama服务可用，已安装模型数: {len(models.get('models', []))}")

        # 检查推荐的模型是否存在
        model_names = [model.get('name', '') for model in models.get('models', [])]
        recommended_models = ['qwen2:7b-instruct', 'qwen3:4b', 'llama3']

        available_recommended = [model for model in recommended_models if any(model in name for name in model_names)]

        if available_recommended:
            print(f"✅ 找到推荐模型: {', '.join(available_recommended)}")
        else:
            print("⚠️ 未找到推荐模型，建议运行:")
            print("   ollama pull qwen2:7b-instruct")
            print("   或 ollama pull qwen3:4b")

        return True

    except ImportError:
        print("❌ ollama包未安装")
        return False
    except Exception as e:
        print(f"❌ Ollama服务不可用: {e}")
        print("请确保Ollama已安装并正在运行")
        print("下载地址: https://ollama.com/")
        return False

def setup_directories():
    """
    设置必要的目录结构

    @returns 无返回值
    """
    directories = [
        "./knowledge_base/",
        "./vector_store/",
        "./data/"
    ]

    for dir_path in directories:
        Path(dir_path).mkdir(exist_ok=True)
        print(f"📁 确保目录存在: {dir_path}")

def copy_sample_data():
    """
    将示例数据复制到知识库目录

    @returns 无返回值
    """
    sample_file = Path("./data/sample_data.xlsx")
    knowledge_base_file = Path("./knowledge_base/sample_data.xlsx")

    if sample_file.exists() and not knowledge_base_file.exists():
        import shutil
        shutil.copy2(sample_file, knowledge_base_file)
        print(f"📄 复制示例数据到知识库: {knowledge_base_file}")
    elif knowledge_base_file.exists():
        print(f"📄 知识库中已存在示例数据: {knowledge_base_file}")
    else:
        print("⚠️ 未找到示例数据文件，请手动上传Excel文件到知识库")

def start_server():
    """
    启动RAG API服务器

    @returns 无返回值
    """
    print("🚀 启动RAG API服务器...")

    try:
        # 使用uvicorn启动服务器
        import uvicorn
        uvicorn.run(
            "rag_api_server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")

def main():
    """
    主函数

    @returns 无返回值
    """
    print("🎯 RAG Excel API服务器启动器")
    print("=" * 50)

    # 1. 检查依赖
    print("1️⃣ 检查Python依赖...")
    if not check_dependencies():
        sys.exit(1)
    print()

    # 2. 检查Ollama
    print("2️⃣ 检查Ollama服务...")
    if not check_ollama():
        print("⚠️ Ollama服务不可用，但服务器仍可启动（聊天功能可能不工作）")
    print()

    # 3. 设置目录
    print("3️⃣ 设置目录结构...")
    setup_directories()
    print()

    # 4. 复制示例数据
    print("4️⃣ 准备示例数据...")
    copy_sample_data()
    print()

    # 5. 启动服务器
    print("5️⃣ 启动API服务器...")
    print("📍 服务地址: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔄 ReDoc文档: http://localhost:8000/redoc")
    print("🧪 测试客户端: python test_api_client.py")
    print()
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)

    start_server()

if __name__ == "__main__":
    main()
