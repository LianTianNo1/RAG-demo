#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流式响应测试脚本

@remarks 测试RAG API的流式响应功能
@author AI Assistant
@version 1.0
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_stream_chat(message: str):
    """
    测试流式聊天功能
    
    @param message - 要发送的消息
    @returns 无返回值
    """
    print(f"🌊 测试流式聊天: {message}")
    print("=" * 60)
    
    payload = {
        "model": "rag-excel",
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.7,
        "stream": True  # 启用流式响应
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            stream=True  # 启用流式接收
        )
        
        if response.status_code == 200:
            print("📡 开始接收流式响应...")
            print()
            
            full_content = ""
            tool_calls = []
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    
                    # 跳过空行和注释行
                    if not line_str.strip() or line_str.startswith(':'):
                        continue
                    
                    # 处理SSE数据
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # 移除 "data: " 前缀
                        
                        # 检查是否是结束标记
                        if data_str.strip() == '[DONE]':
                            print("\n✅ 流式响应完成")
                            break
                        
                        try:
                            data = json.loads(data_str)
                            
                            if 'choices' in data and len(data['choices']) > 0:
                                choice = data['choices'][0]
                                delta = choice.get('delta', {})
                                
                                # 处理内容
                                if 'content' in delta and delta['content']:
                                    content = delta['content']
                                    print(content, end='', flush=True)
                                    full_content += content
                                
                                # 处理工具调用
                                if 'tool_calls' in delta:
                                    for tool_call in delta['tool_calls']:
                                        tool_name = tool_call.get('function', {}).get('name', 'unknown')
                                        tool_args = tool_call.get('function', {}).get('arguments', '{}')
                                        
                                        print(f"\n🔧 工具调用: {tool_name}")
                                        try:
                                            args_dict = json.loads(tool_args)
                                            for key, value in args_dict.items():
                                                print(f"   {key}: {value}")
                                        except:
                                            print(f"   参数: {tool_args}")
                                        print()
                                        
                                        tool_calls.append(tool_call)
                                
                                # 检查是否完成
                                if choice.get('finish_reason') == 'stop':
                                    print("\n✅ 生成完成")
                                    break
                        
                        except json.JSONDecodeError as e:
                            print(f"\n⚠️ JSON解析错误: {e}")
                            print(f"原始数据: {data_str}")
            
            print("\n" + "=" * 60)
            print(f"📊 完整内容长度: {len(full_content)} 字符")
            print(f"🔧 工具调用数量: {len(tool_calls)}")
            
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 流式测试异常: {e}")

def test_non_stream_chat(message: str):
    """
    测试非流式聊天功能（对比）
    
    @param message - 要发送的消息
    @returns 无返回值
    """
    print(f"📄 测试非流式聊天: {message}")
    print("=" * 60)
    
    payload = {
        "model": "rag-excel",
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.7,
        "stream": False  # 非流式响应
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            choice = data['choices'][0]
            message_content = choice['message']['content']
            
            print(f"🤖 助手回答:")
            print(message_content)
            
            # 显示工具调用信息
            if 'tool_calls' in choice['message']:
                print(f"\n🔧 工具调用:")
                for tool_call in choice['message']['tool_calls']:
                    func_name = tool_call['function']['name']
                    func_args = json.loads(tool_call['function']['arguments'])
                    print(f"   🛠️ {func_name}: {func_args}")
            
            # 显示性能信息
            usage = data['usage']
            print(f"\n📊 性能统计:")
            print(f"   响应时间: {end_time - start_time:.2f} 秒")
            print(f"   Token使用: 输入={usage['prompt_tokens']}, 输出={usage['completion_tokens']}, 总计={usage['total_tokens']}")
            
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 非流式测试异常: {e}")

def main():
    """
    主测试函数
    
    @returns 无返回值
    """
    print("🧪 RAG API 流式响应测试")
    print("请确保API服务器正在运行 (python rag_api_server.py)")
    print()
    
    # 检查服务器连接
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API服务器不可用")
            return
        print("✅ API服务器连接正常")
        print()
    except Exception as e:
        print(f"❌ 无法连接到API服务器: {e}")
        return
    
    test_questions = [
        "张三在哪个部门？他的薪资是多少？",
        "技术部有哪些员工？请详细介绍他们的情况。",
        "请总结一下所有项目的情况，包括负责人和状态。"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*80}")
        print(f"测试问题 {i}: {question}")
        print('='*80)
        
        # 测试流式响应
        test_stream_chat(question)
        
        print("\n" + "-" * 80)
        
        # 测试非流式响应（对比）
        test_non_stream_chat(question)
        
        if i < len(test_questions):
            print("\n⏳ 等待3秒后继续下一个测试...")
            time.sleep(3)
    
    print(f"\n{'='*80}")
    print("✅ 所有测试完成")
    print("🌐 Web界面: http://localhost:8000/web_demo.html")
    print("📖 API文档: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
