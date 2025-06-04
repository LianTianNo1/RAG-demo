# Excel RAG系统

这是一个基于检索增强生成(RAG)的系统，能够从Excel文件中检索信息并使用本地Ollama大语言模型来回答用户问题。

## 功能特点

- 📊 **Excel文件处理**: 自动读取指定目录下的所有Excel文件和工作表
- 🔍 **智能检索**: 使用向量数据库(FAISS)进行语义相似度检索
- 🤖 **本地大模型**: 集成Ollama本地大语言模型，支持中文问答
- 💬 **交互式问答**: 支持命令行交互式问答界面
- 🧪 **自动测试**: 内置测试功能，自动验证系统功能

## 项目结构

```
RAG_TEST/
├── rag_excel.py              # 主要的Python代码
├── install_dependencies.sh   # 依赖安装脚本
├── create_sample_data.py     # 创建示例数据的脚本
├── data/                     # 存放Excel文件的目录
│   └── sample_data.xlsx      # 示例Excel文件
└── README.md                 # 项目说明文档
```

## 安装和使用

### 1. 安装Ollama并拉取模型

首先访问 [https://ollama.com/](https://ollama.com/) 下载并安装Ollama。

然后在终端中运行以下命令拉取推荐的中文模型：

```bash
ollama pull qwen2:7b-instruct
```

或者拉取其他模型：

```bash
ollama pull llama3
```

确保Ollama服务正在运行。

### 2. 安装Python依赖

在项目根目录下运行：

```bash
# Windows (PowerShell)
.\install_dependencies.sh

# Linux/macOS
bash install_dependencies.sh
```

或者手动安装：

```bash
pip install pandas openpyxl sentence-transformers faiss-cpu langchain langchain-community langchain-text-splitters ollama
```

### 3. 准备Excel数据

将你的Excel文件放入 `data/` 目录下。系统会自动读取该目录下的所有 `.xlsx` 文件。

如果没有Excel文件，可以运行以下命令创建示例数据：

```bash
python create_sample_data.py
```

### 4. 运行RAG系统

```bash
python rag_excel.py
```

程序会首先运行测试模式，然后进入交互式问答模式。

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
