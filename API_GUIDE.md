# RAG Excel API 使用指南

## 🎯 项目概述

这是一个基于FastAPI的RAG（检索增强生成）API服务，专门用于处理Excel文件并提供智能问答功能。系统提供标准的OpenAI兼容接口，支持工具调用展示，具有智能缓存和文件监控功能。

## 🚀 核心特性

### 1. 标准API接口
- **兼容OpenAI格式**: `/v1/chat/completions` 接口
- **工具调用展示**: 类似MCP，显示 `excel_search` 和 `llm_generate` 工具使用情况
- **完整响应**: 包含工具调用信息、来源文件、token使用统计

### 2. 智能RAG系统
- **文件变化检测**: 只在文件修改时重新构建向量库
- **向量缓存**: 持久化存储，避免重复计算
- **增量更新**: 支持文件添加、删除的智能更新

### 3. 文件管理
- **上传接口**: 支持Excel文件上传到知识库
- **文件列表**: 查看知识库中的所有文件
- **文件删除**: 删除指定文件并自动更新向量库

## 📡 API接口详解

### 聊天接口

**请求格式**:
```http
POST /v1/chat/completions
Content-Type: application/json

{
  "model": "rag-excel",
  "messages": [
    {"role": "user", "content": "张三在哪个部门？他的薪资是多少？"}
  ],
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**响应格式**:
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
        "content": "根据提供的信息，张三在技术部工作，担任软件工程师职位，薪资为15万。\n\n📚 **信息来源:**\n1. 文件: sample_data.xlsx, 工作表: 员工信息\n",
        "tool_calls": [
          {
            "id": "call_20241201_123456",
            "type": "function",
            "function": {
              "name": "excel_search",
              "arguments": "{\"query\": \"张三在哪个部门？他的薪资是多少？\", \"files\": \"all\", \"top_k\": 3}"
            }
          },
          {
            "id": "call_20241201_123456_llm",
            "type": "function",
            "function": {
              "name": "llm_generate",
              "arguments": "{\"context\": \"姓名: 张三, 部门: 技术部, 职位: 软件工程师...\", \"question\": \"张三在哪个部门？他的薪资是多少？\", \"model\": \"qwen2:7b-instruct\"}"
            }
          }
        ]
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 45,
    "total_tokens": 70
  }
}
```

### 文件上传接口

**请求格式**:
```http
POST /v1/files/upload
Content-Type: multipart/form-data

file: [Excel文件]
```

**响应格式**:
```json
{
  "success": true,
  "filename": "employees.xlsx",
  "file_id": "file_20241201_123456_a1b2c3d4",
  "message": "文件 employees.xlsx 上传成功，正在后台更新知识库...",
  "file_hash": "a1b2c3d4e5f6g7h8"
}
```

### 其他接口

#### 健康检查
```http
GET /health
```

#### 文件列表
```http
GET /v1/files/list
```

#### 删除文件
```http
DELETE /v1/files/{filename}
```

#### 重建向量库
```http
POST /v1/vector_store/rebuild
```

## 🔧 工具调用说明

系统模拟了两个主要工具：

### 1. excel_search 工具
- **功能**: 在Excel文件中搜索相关信息
- **参数**:
  - `query`: 搜索查询
  - `files`: 指定文件列表或"all"
  - `top_k`: 返回结果数量

### 2. llm_generate 工具
- **功能**: 使用大语言模型生成答案
- **参数**:
  - `context`: 检索到的上下文信息
  - `question`: 用户问题
  - `model`: 使用的模型名称

## 🎮 使用示例

### Python客户端示例

```python
import requests

# 聊天请求
def chat_with_rag(message):
    response = requests.post(
        "http://localhost:8000/v1/chat/completions",
        json={
            "model": "rag-excel",
            "messages": [{"role": "user", "content": message}],
            "temperature": 0.7
        }
    )
    return response.json()

# 文件上传
def upload_file(file_path):
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(
            "http://localhost:8000/v1/files/upload",
            files=files
        )
    return response.json()

# 使用示例
result = chat_with_rag("技术部有哪些员工？")
print(result["choices"][0]["message"]["content"])

# 查看工具调用
for tool_call in result["choices"][0]["message"].get("tool_calls", []):
    print(f"工具: {tool_call['function']['name']}")
    print(f"参数: {tool_call['function']['arguments']}")
```

### JavaScript客户端示例

```javascript
// 聊天请求
async function chatWithRAG(message) {
    const response = await fetch('http://localhost:8000/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: 'rag-excel',
            messages: [{role: 'user', content: message}],
            temperature: 0.7
        })
    });
    return await response.json();
}

// 文件上传
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('http://localhost:8000/v1/files/upload', {
        method: 'POST',
        body: formData
    });
    return await response.json();
}

// 使用示例
chatWithRAG("Alpha项目的负责人是谁？").then(result => {
    console.log(result.choices[0].message.content);
    
    // 显示工具调用
    const toolCalls = result.choices[0].message.tool_calls || [];
    toolCalls.forEach(toolCall => {
        console.log(`工具: ${toolCall.function.name}`);
        console.log(`参数: ${toolCall.function.arguments}`);
    });
});
```

## 🔍 前端集成建议

### 工具调用展示
在前端界面中，可以这样展示工具调用信息：

```html
<div class="tool-calls">
    <h4>🔧 工具调用</h4>
    <div class="tool-call">
        <span class="tool-name">excel_search</span>
        <div class="tool-args">
            查询: "张三在哪个部门？"<br>
            文件: 全部<br>
            结果数: 3
        </div>
    </div>
    <div class="tool-call">
        <span class="tool-name">llm_generate</span>
        <div class="tool-args">
            模型: qwen2:7b-instruct<br>
            上下文长度: 500字符
        </div>
    </div>
</div>
```

### 来源信息展示
```html
<div class="sources">
    <h4>📚 信息来源</h4>
    <ul>
        <li>文件: sample_data.xlsx, 工作表: 员工信息</li>
        <li>文件: sample_data.xlsx, 工作表: 项目信息</li>
    </ul>
</div>
```

## 🚀 部署建议

### 开发环境
```bash
python rag_api_server.py
```

### 生产环境
```bash
uvicorn rag_api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "rag_api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📊 性能优化

1. **向量缓存**: 系统自动缓存向量数据库，避免重复计算
2. **文件监控**: 只在文件变化时更新，提升响应速度
3. **异步处理**: 使用FastAPI的异步特性，支持高并发
4. **后台任务**: 文件上传后在后台更新向量库，不阻塞响应

## 🔒 安全考虑

1. **文件类型限制**: 只允许上传Excel文件
2. **文件大小限制**: 可在FastAPI中配置最大文件大小
3. **CORS配置**: 生产环境中应限制允许的域名
4. **输入验证**: 对用户输入进行验证和清理
