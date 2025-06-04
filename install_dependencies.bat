@echo off
chcp 65001 >nul
echo 正在安装Python RAG示例所需的依赖库...
echo.

echo 正在安装依赖库...
pip install pandas openpyxl sentence-transformers faiss-cpu langchain langchain-community langchain-text-splitters ollama

echo.
echo 依赖安装完成。
echo.
echo 请确保你已经安装并运行了Ollama服务，并且拉取了至少一个模型，例如：
echo ollama pull qwen2:7b-instruct  (推荐，中文能力较好)
echo 或者
echo ollama pull llama3
echo.
echo 你可以在 rag_excel.py 文件中修改 LLM_MODEL_NAME 来指定使用的模型。
echo.
pause
