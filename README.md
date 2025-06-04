# Excel RAG API系统

这是一个基于检索增强生成(RAG)的API服务，能够从Excel文件中检索信息并使用本地Ollama大语言模型来回答用户问题。系统提供标准的REST API接口，支持文件上传、智能问答等功能。

## 🚀 版本更新

### v2.0 - API服务版本
- ✨ **标准API接口**: 提供兼容OpenAI格式的 `/v1/chat/completions` 接口
- 📤 **文件上传**: 支持通过API上传Excel文件到知识库
- 🔧 **工具调用展示**: 类似MCP，显示工具使用信息（excel_search、llm_generate）
- 🎯 **智能RAG触发**: 只在文件变化时重新构建向量库，提升性能
- 🌐 **Web演示界面**: 提供可视化的文件上传和聊天界面
- 📊 **文件管理**: 支持文件列表查看、删除等操作
- ⚡ **异步处理**: 使用FastAPI提供高性能异步服务

### v1.0 - 命令行版本
- 📊 **Excel文件处理**: 自动读取指定目录下的所有Excel文件和工作表
- 🔍 **智能检索**: 使用向量数据库(FAISS)进行语义相似度检索
- 🤖 **本地大模型**: 集成Ollama本地大语言模型，支持中文问答
- 💬 **交互式问答**: 支持命令行交互式问答界面
- 🧪 **自动测试**: 内置测试功能，自动验证系统功能

## 功能特点

### 🎯 核心功能
- **标准API接口**: 兼容OpenAI格式的聊天接口
- **文件上传管理**: 支持Excel文件上传、列表查看、删除
- **智能RAG检索**: 基于文件内容的语义检索
- **工具调用展示**: 显示excel_search和llm_generate工具使用情况
- **性能优化**: 智能缓存，只在文件变化时重建向量库

### 🔧 技术特性
- **异步处理**: FastAPI提供高性能异步服务
- **文件监控**: 自动检测文件变化，智能更新向量库
- **向量缓存**: 持久化向量数据库，避免重复计算
- **错误处理**: 完善的异常处理和错误提示
- **CORS支持**: 支持跨域请求，便于前端集成

## 项目结构

```
RAG_TEST/
├── rag_api_server.py         # 🚀 主要的API服务器 (v2.0)
├── rag_excel.py              # 📜 命令行版本 (v1.0)
├── test_api_client.py        # 🧪 API客户端测试脚本
├── start_server.py           # ⚡ 服务器启动脚本
├── web_demo.html             # 🌐 Web演示界面
├── install_dependencies.sh   # 🐧 Linux/macOS依赖安装脚本
├── install_dependencies.bat  # 🪟 Windows依赖安装脚本
├── create_sample_data.py     # 📊 创建示例数据的脚本
├── create_excel_simple.py    # 📄 简单Excel创建脚本
├── data/                     # 📁 示例数据目录
│   ├── sample_data.xlsx      # 示例Excel文件
│   ├── employees.csv         # 员工信息CSV
│   └── projects.csv          # 项目信息CSV
├── knowledge_base/           # 🗄️ 知识库文件存储目录 (运行时创建)
├── vector_store/             # 🔍 向量数据库存储目录 (运行时创建)
├── README.md                 # 📖 项目说明文档
└── QUICK_START.md           # 🚀 快速开始指南
```

## 🚀 快速开始

### 方法一：一键启动 (推荐)

```bash
# 1. 安装依赖
pip install fastapi uvicorn pandas openpyxl sentence-transformers faiss-cpu langchain langchain-community langchain-text-splitters ollama python-multipart watchdog

# 2. 安装并启动Ollama qwen3:8b qwen3:4b
ollama pull qwen3:8b

# 3. 启动服务器
python start_server.py
```

### 方法二：手动启动

#### 1. 安装Ollama并拉取模型

访问 [https://ollama.com/](https://ollama.com/) 下载并安装Ollama。

```bash
# 拉取推荐的中文模型
ollama pull qwen3:8b

# 或者拉取其他模型
ollama pull qwen3:4b
ollama pull llama3
```

#### 2. 安装Python依赖

```bash
# Windows
install_dependencies.bat

# Linux/macOS
bash install_dependencies.sh

# 或手动安装
pip install fastapi uvicorn pandas openpyxl sentence-transformers faiss-cpu langchain langchain-community langchain-text-splitters ollama python-multipart watchdog
```

#### 3. 启动API服务器

```bash
# 直接启动
python rag_api_server.py

# 或使用启动脚本（包含环境检查）
python start_server.py
```

#### 4. 访问服务

- 🌐 **Web演示界面**: http://localhost:8000/web_demo.html
- 📖 **API文档**: http://localhost:8000/docs
- 🔄 **ReDoc文档**: http://localhost:8000/redoc
- 🧪 **测试客户端**: `python test_api_client.py`

## 📡 API接口说明

### 聊天接口 (兼容OpenAI格式)

```bash
POST /v1/chat/completions
Content-Type: application/json

{
  "model": "rag-excel",
  "messages": [
    {"role": "user", "content": "张三在哪个部门？"}
  ],
  "temperature": 0.7
}
```

**响应示例**:
```json
{
  "id": "chatcmpl-20241201123456",
  "object": "chat.completion",
  "created": 1701234567,
  "model": "rag-excel",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "根据提供的信息，张三在技术部工作...",
        "tool_calls": [
          {
            "id": "call_20241201_123456",
            "type": "function",
            "function": {
              "name": "excel_search",
              "arguments": "{\"query\": \"张三在哪个部门？\", \"files\": \"all\", \"top_k\": 3}"
            }
          }
        ]
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 25,
    "total_tokens": 40
  }
}
```

### 文件上传接口

```bash
POST /v1/files/upload
Content-Type: multipart/form-data

# 上传Excel文件
curl -X POST "http://localhost:8000/v1/files/upload" \
     -F "file=@your_file.xlsx"
```

### 其他接口

- `GET /health` - 健康检查
- `GET /v1/files/list` - 文件列表
- `DELETE /v1/files/{filename}` - 删除文件
- `POST /v1/vector_store/rebuild` - 重建向量库

## 使用示例

### 示例问题

基于示例数据，你可以尝试以下问题：

- "张三在哪个部门？他的薪资是多少？"
- "Alpha项目的负责人是谁？"
- "技术部有哪些员工？"
- "哪个项目的预算最高？"
- "市场部的平均薪资是多少？"

### 示例对话

```
请输入你的问题: 张三在哪个部门？
回答: 根据提供的信息，张三在技术部工作，担任软件工程师职位。

请输入你的问题: Alpha项目的负责人是谁？
回答: Alpha项目的负责人是王五。

请输入你的问题: 退出
感谢使用，再见！
```

## 配置说明

在 `rag_excel.py` 文件中，你可以修改以下配置：

```python
# Excel文件所在的目录路径
EXCEL_FILES_DIRECTORY = "./data/"

# 使用的嵌入模型
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# 使用的Ollama大语言模型
LLM_MODEL_NAME = "qwen2:7b-instruct"

# 文本切分配置
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
```

## 系统架构

### RAG流程

1. **数据加载**: 读取Excel文件，将每个工作表转换为文本
2. **文本分割**: 将长文本切分成适合处理的小块
3. **向量化**: 使用嵌入模型将文本转换为向量
4. **构建索引**: 使用FAISS构建向量数据库
5. **问题检索**: 根据用户问题检索最相关的文本块
6. **答案生成**: 将检索结果和问题发送给大语言模型生成答案

### 核心组件

- **ExcelRAGSystem**: 主要的RAG系统类
- **HuggingFace Embeddings**: 文本向量化
- **FAISS**: 向量数据库和相似度检索
- **Ollama**: 本地大语言模型
- **Langchain**: RAG流程编排

## 故障排除

### 常见问题

1. **Ollama连接失败**
   - 确保Ollama服务正在运行
   - 确保已经拉取了指定的模型
   - 检查模型名称是否正确

2. **依赖安装失败**
   - 尝试使用虚拟环境
   - 检查Python版本（推荐3.8+）
   - 如果有GPU，可以安装 `faiss-gpu` 替代 `faiss-cpu`

3. **Excel文件读取失败**
   - 确保Excel文件格式正确（.xlsx）
   - 检查文件是否被其他程序占用
   - 确保文件路径正确

4. **内存不足**
   - 减少 `CHUNK_SIZE` 的值
   - 使用更小的嵌入模型
   - 分批处理大型Excel文件

## 扩展功能

### 支持更多文件格式

可以扩展系统以支持：
- CSV文件
- Word文档
- PDF文件
- 纯文本文件

### 高级检索

可以添加：
- 混合检索（关键词+语义）
- 重排序模型
- 查询扩展
- 多轮对话支持

### 部署选项

- Web界面（Streamlit/Gradio）
- API服务（FastAPI）
- Docker容器化
- 云端部署

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。
