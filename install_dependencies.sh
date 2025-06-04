#!/bin/bash

# 脚本功能：安装Python RAG示例所需的依赖库

echo "正在创建并激活虚拟环境 (可选，但推荐)..."
# 你可以取消下面两行的注释来使用虚拟环境
# python3 -m venv rag_env
# source rag_env/bin/activate

echo "正在安装依赖库..."
pip install pandas openpyxl sentence-transformers faiss-cpu langchain langchain-community langchain-text-splitters ollama

# 如果你的机器有NVIDIA GPU并且安装了CUDA，可以考虑安装 faiss-gpu 以获得更好的性能
# pip install faiss-gpu

echo "依赖安装完成。"
echo "请确保你已经安装并运行了Ollama服务，并且拉取了至少一个模型，例如："
echo "ollama pull qwen2:7b-instruct  (推荐，中文能力较好)"
echo "或者"
echo "ollama pull llama3"
echo "你可以在 rag_excel.py 文件中修改 LLM_MODEL_NAME 来指定使用的模型。"
