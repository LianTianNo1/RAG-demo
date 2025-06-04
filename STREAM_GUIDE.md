# RAG Excel API 流式响应指南

## 🌊 流式响应功能

RAG Excel API现在支持Server-Sent Events (SSE)格式的流式响应，可以实时看到AI的思考和回答过程。

## 🚀 功能特点

### 1. 实时流式输出
- ✅ **工具调用展示**: 实时显示 `excel_search` 和 `llm_generate` 工具的使用
- ✅ **检索过程**: 显示文档检索的进度和结果
- ✅ **逐字生成**: 模拟真实的AI思考过程，逐步输出答案
- ✅ **来源信息**: 在回答末尾显示信息来源

### 2. 兼容性
- ✅ **OpenAI格式**: 完全兼容OpenAI的流式响应格式
- ✅ **向下兼容**: 同时支持流式和非流式响应
- ✅ **标准SSE**: 使用标准的Server-Sent Events协议

## 📡 API使用方法

### 启用流式响应

只需在请求中添加 `"stream": true` 参数：

```json
{
  "model": "rag-excel",
  "messages": [
    {"role": "user", "content": "张三在哪个部门？"}
  ],
  "temperature": 0.7,
  "stream": true
}
```

### 响应格式

流式响应使用SSE格式，每个数据块的格式如下：

```
data: {"id":"chatcmpl-20241201123456","object":"chat.completion.chunk","created":1701234567,"model":"rag-excel","choices":[{"index":0,"delta":{"content":"张三"},"finish_reason":null}]}

data: {"id":"chatcmpl-20241201123456","object":"chat.completion.chunk","created":1701234567,"model":"rag-excel","choices":[{"index":0,"delta":{"content":"在"},"finish_reason":null}]}

data: [DONE]
```

## 🔧 工具调用流程

流式响应会按以下顺序展示完整的RAG流程：

### 1. 工具调用阶段
```json
{
  "choices": [{
    "delta": {
      "tool_calls": [{
        "id": "call_20241201_123456",
        "type": "function",
        "function": {
          "name": "excel_search",
          "arguments": "{\"query\": \"张三在哪个部门？\", \"files\": \"all\", \"top_k\": 3}"
        }
      }]
    }
  }]
}
```

### 2. 检索结果阶段
```json
{
  "choices": [{
    "delta": {
      "content": "🔍 检索到 2 个相关文档\n"
    }
  }]
}
```

### 3. LLM生成工具调用
```json
{
  "choices": [{
    "delta": {
      "tool_calls": [{
        "id": "call_20241201_123456_llm",
        "type": "function",
        "function": {
          "name": "llm_generate",
          "arguments": "{\"model\": \"qwen2:7b-instruct\", \"context\": \"...\"}"
        }
      }]
    }
  }]
}
```

### 4. 内容生成阶段
```json
{
  "choices": [{
    "delta": {
      "content": "根据提供的信息，"
    }
  }]
}
```

### 5. 来源信息阶段
```json
{
  "choices": [{
    "delta": {
      "content": "\n\n📚 **信息来源:**\n1. 文件: sample_data.xlsx, 工作表: 员工信息\n"
    }
  }]
}
```

### 6. 完成阶段
```json
{
  "choices": [{
    "delta": {},
    "finish_reason": "stop"
  }]
}
```

## 💻 客户端实现示例

### Python客户端

```python
import requests
import json

def stream_chat(message):
    payload = {
        "model": "rag-excel",
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.7,
        "stream": True
    }

    response = requests.post(
        "http://localhost:8000/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        json=payload,
        stream=True
    )

    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_str = line_str[6:]
                if data_str.strip() == '[DONE]':
                    break

                try:
                    data = json.loads(data_str)
                    if 'choices' in data and data['choices']:
                        choice = data['choices'][0]
                        delta = choice.get('delta', {})

                        # 处理内容
                        if 'content' in delta:
                            print(delta['content'], end='', flush=True)

                        # 处理工具调用
                        if 'tool_calls' in delta:
                            for tool_call in delta['tool_calls']:
                                print(f"\n🔧 {tool_call['function']['name']}")

                except json.JSONDecodeError:
                    pass

# 使用示例
stream_chat("张三在哪个部门？")
```

### JavaScript客户端

```javascript
async function streamChat(message) {
    const response = await fetch('http://localhost:8000/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: 'rag-excel',
            messages: [{role: 'user', content: message}],
            temperature: 0.7,
            stream: true
        })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const dataStr = line.slice(6);
                if (dataStr.trim() === '[DONE]') return;

                try {
                    const data = JSON.parse(dataStr);
                    if (data.choices && data.choices[0]) {
                        const delta = data.choices[0].delta;

                        // 处理内容
                        if (delta.content) {
                            document.getElementById('output').textContent += delta.content;
                        }

                        // 处理工具调用
                        if (delta.tool_calls) {
                            console.log('工具调用:', delta.tool_calls);
                        }
                    }
                } catch (e) {
                    console.warn('解析错误:', e);
                }
            }
        }
    }
}

// 使用示例
streamChat("技术部有哪些员工？");
```

## 🌐 Web界面集成

Web演示界面 (`web_demo.html`) 已经完全支持流式响应：

1. **实时显示**: 答案会逐字显示，就像AI在实时思考
2. **工具调用展示**: 显示使用的工具和参数
3. **自动滚动**: 聊天窗口自动滚动到最新内容
4. **错误处理**: 完善的错误处理和重连机制

## 🔍 调试和监控

### 服务器日志
服务器会记录所有流式请求：
```
INFO: 127.0.0.1:51320 - "POST /v1/chat/completions HTTP/1.1" 200 OK
```

### 客户端调试
在浏览器开发者工具中可以看到SSE连接：
- Network标签页中查看EventStream类型的请求
- Console中查看解析的数据块

## ⚡ 性能优化

1. **分块大小**: 默认每3个词为一块，可调整以平衡实时性和性能
2. **延迟控制**: 每块之间有0.1秒延迟，模拟真实生成过程
3. **缓冲机制**: 客户端使用缓冲区处理不完整的数据行
4. **连接复用**: 支持HTTP/1.1的keep-alive连接

## 🚀 使用建议

1. **前端集成**: 使用EventSource API或fetch stream处理SSE
2. **错误处理**: 实现重连机制处理网络中断
3. **用户体验**: 显示加载状态和进度指示器
4. **性能监控**: 监控流式响应的延迟和吞吐量

## 🎯 示例场景

### 场景1: 简单查询
```
用户: "张三在哪个部门？"

流式输出:
🔧 excel_search: {"query": "张三在哪个部门？", "files": "all", "top_k": 3}
🔍 检索到 1 个相关文档
🤖 正在生成回答...
🔧 llm_generate: {"model": "qwen2:7b-instruct", "context": "..."}
根据提供的信息，张三在技术部工作，担任软件工程师职位。

📚 **信息来源:**
1. 文件: sample_data.xlsx, 工作表: 员工信息
```

### 场景2: 复杂分析
```
用户: "请分析一下技术部的人员构成和薪资情况"

流式输出:
🔧 excel_search: {"query": "技术部人员构成薪资", "files": "all", "top_k": 5}
🔍 检索到 3 个相关文档
🤖 正在生成回答...
🔧 llm_generate: {"model": "qwen2:7b-instruct", "context": "..."}
根据提供的数据，技术部目前有2名员工：

1. 张三 - 软件工程师，薪资15万
2. 王五 - 项目经理，薪资18万

技术部平均薪资为16.5万，是公司薪资水平较高的部门...

📚 **信息来源:**
1. 文件: sample_data.xlsx, 工作表: 员工信息
2. 文件: sample_data.xlsx, 工作表: 部门统计
```


