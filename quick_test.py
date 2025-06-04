#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 验证RAG API是否正常工作

@remarks 简单快速的API功能测试
@author AI Assistant
@version 1.0
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_api():
    """
    快速测试API功能
    
    @returns 无返回值
    """
    print("🧪 RAG API 快速测试")
    print("=" * 40)
    
    # 1. 健康检查
    print("1️⃣ 测试健康检查...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务状态: {data['status']}")
            print(f"📊 向量库就绪: {data['vector_store_ready']}")
            print(f"📁 知识库文件数: {data['knowledge_base_files']}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 无法连接到API服务器: {e}")
        print("请确保服务器正在运行: python start_server.py")
        return
    
    print()
    
    # 2. 测试聊天功能
    print("2️⃣ 测试聊天功能...")
    test_questions = [
        "你好，请介绍一下你的功能",
        "张三在哪个部门？",
        "技术部有哪些员工？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 问题 {i}: {question}")
        try:
            payload = {
                "model": "rag-excel",
                "messages": [{"role": "user", "content": question}],
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{API_BASE_URL}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data['choices'][0]['message']['content']
                print(f"🤖 回答: {answer[:200]}{'...' if len(answer) > 200 else ''}")
                
                # 显示工具调用（如果有）
                tool_calls = data['choices'][0]['message'].get('tool_calls', [])
                if tool_calls:
                    print(f"🔧 使用了 {len(tool_calls)} 个工具:")
                    for tool_call in tool_calls:
                        print(f"   - {tool_call['function']['name']}")
                
                # 显示token使用
                usage = data.get('usage', {})
                print(f"📊 Token: {usage.get('total_tokens', 0)}")
                
            else:
                print(f"❌ 聊天失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except Exception as e:
            print(f"❌ 聊天异常: {e}")
        
        time.sleep(1)  # 避免请求过快
    
    print()
    print("=" * 40)
    print("✅ 快速测试完成")
    print()
    print("🌐 Web界面: http://localhost:8000/web_demo.html")
    print("📖 API文档: http://localhost:8000/docs")
    print("🧪 完整测试: python test_api_client.py")

if __name__ == "__main__":
    test_api()
