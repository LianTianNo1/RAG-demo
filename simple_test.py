import requests
import json

# 测试健康检查
print("测试健康检查...")
response = requests.get("http://localhost:8000/health")
print(f"状态码: {response.status_code}")
print(f"响应: {response.json()}")
print()

# 测试聊天
print("测试聊天...")
payload = {
    "model": "rag-excel",
    "messages": [{"role": "user", "content": "张三在哪个部门？"}],
    "temperature": 0.7
}

response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    headers={"Content-Type": "application/json"},
    json=payload
)

print(f"状态码: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"回答: {data['choices'][0]['message']['content']}")
    
    # 显示工具调用
    tool_calls = data['choices'][0]['message'].get('tool_calls', [])
    if tool_calls:
        print(f"工具调用数量: {len(tool_calls)}")
        for tool_call in tool_calls:
            print(f"  - {tool_call['function']['name']}")
else:
    print(f"错误: {response.text}")
