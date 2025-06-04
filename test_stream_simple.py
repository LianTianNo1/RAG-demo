import requests
import json

def test_stream():
    print("测试流式响应...")
    
    payload = {
        "model": "rag-excel",
        "messages": [{"role": "user", "content": "张三在哪个部门？"}],
        "temperature": 0.7,
        "stream": True
    }
    
    response = requests.post(
        "http://localhost:8000/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        json=payload,
        stream=True
    )
    
    print(f"状态码: {response.status_code}")
    print("流式响应内容:")
    print("-" * 50)
    
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            print(f"原始行: {line_str}")
            
            if line_str.startswith('data: '):
                data_str = line_str[6:]
                if data_str.strip() == '[DONE]':
                    print("流式响应结束")
                    break
                
                try:
                    data = json.loads(data_str)
                    if 'choices' in data and data['choices']:
                        choice = data['choices'][0]
                        delta = choice.get('delta', {})
                        if 'content' in delta:
                            print(f"内容: {delta['content']}")
                except Exception as e:
                    print(f"解析错误: {e}")

if __name__ == "__main__":
    test_stream()
