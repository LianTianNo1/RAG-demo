# 快速开始指南

## 🚀 快速安装和运行

### 1. 安装Ollama
访问 [https://ollama.com/](https://ollama.com/) 下载并安装Ollama

### 2. 拉取中文模型
```bash
ollama pull qwen2:7b-instruct
```

### 3. 安装Python依赖
```bash
pip install pandas openpyxl sentence-transformers faiss-cpu langchain langchain-community langchain-text-splitters ollama
```

### 4. 运行RAG系统
```bash
python rag_excel.py
```

## 📝 使用说明

### 测试模式
程序首先会运行测试模式，自动创建测试数据并验证系统功能。

### 交互模式
测试完成后，程序会进入交互式问答模式，你可以：

1. 输入问题，例如：
   - "张三在哪个部门？"
   - "Alpha项目的负责人是谁？"
   - "技术部有哪些员工？"

2. 输入 "退出" 结束程序

### 自定义数据
将你的Excel文件放入 `data/` 目录，系统会自动读取所有 `.xlsx` 文件。

## 🔧 配置选项

在 `rag_excel.py` 中可以修改：

- `LLM_MODEL_NAME`: 更改使用的Ollama模型
- `EMBEDDING_MODEL_NAME`: 更改嵌入模型
- `EXCEL_FILES_DIRECTORY`: 更改Excel文件目录
- `CHUNK_SIZE`: 调整文本块大小

## ❗ 常见问题

1. **Ollama连接失败**: 确保Ollama服务正在运行
2. **模型未找到**: 运行 `ollama list` 检查已安装的模型
3. **依赖安装失败**: 考虑使用虚拟环境
4. **内存不足**: 减少 `CHUNK_SIZE` 的值

## 📁 项目文件说明

- `rag_excel.py`: 主程序
- `data/sample_data.xlsx`: 示例Excel文件
- `install_dependencies.sh`: 依赖安装脚本
- `create_excel_simple.py`: 创建示例Excel文件的脚本
