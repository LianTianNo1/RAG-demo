#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真正流式响应测试脚本

@remarks 测试RAG API的真正流式响应功能，对比模拟流式和真实流式的差异
@author AI Assistant
@version 1.0
"""

import requests
import json
import time
import asyncio

API_BASE_URL = "http://localhost:8000"

def test_real_stream_chat(message: str):
    """
    测试真正的流式聊天功能
    
    @param message - 要发送的消息
    @returns 无返回值
    """
    print(f"🌊 测试真正流式聊天: {message}")
    print("=" * 80)
    
    payload = {
        "model": "rag-excel",
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.7,
        "stream": True  # 启用流式响应
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            stream=True  # 启用流式接收
        )
        
        if response.status_code == 200:
            print("📡 开始接收真正的流式响应...")
            print()
            
            full_content = ""
            tool_calls = []
            first_content_time = None
            chunk_count = 0
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # 移除 'data: ' 前缀
                        
                        if data_str.strip() == '[DONE]':
                            print("\n🏁 流式响应完成")
                            break
                        
                        try:
                            data = json.loads(data_str)
                            
                            # 处理不同类型的响应
                            if 'choices' in data and data['choices']:
                                choice = data['choices'][0]
                                delta = choice.get('delta', {})
                                
                                # 处理内容
                                if 'content' in delta and delta['content']:
                                    content = delta['content']
                                    full_content += content
                                    chunk_count += 1
                                    
                                    # 记录第一个内容块的时间
                                    if first_content_time is None:
                                        first_content_time = time.time()
                                        print(f"⏱️ 首个内容块延迟: {first_content_time - start_time:.2f}秒")
                                        print("📝 开始接收内容:")
                                        print("-" * 40)
                                    
                                    # 实时显示内容
                                    print(content, end='', flush=True)
                                
                                # 处理工具调用
                                if 'tool_calls' in delta:
                                    for tool_call in delta['tool_calls']:
                                        tool_calls.append(tool_call)
                                        print(f"\n🔧 工具调用: {tool_call.get('function', {}).get('name', 'unknown')}")
                                        
                        except json.JSONDecodeError as e:
                            print(f"\n⚠️ JSON解析错误: {e}")
                            print(f"原始数据: {data_str}")
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print("\n" + "=" * 80)
            print("📊 流式响应统计:")
            print(f"   总耗时: {total_time:.2f}秒")
            if first_content_time:
                print(f"   首个内容延迟: {first_content_time - start_time:.2f}秒")
                print(f"   内容生成时间: {end_time - first_content_time:.2f}秒")
            print(f"   内容块数量: {chunk_count}")
            print(f"   完整内容长度: {len(full_content)} 字符")
            print(f"   工具调用数量: {len(tool_calls)}")
            if chunk_count > 0:
                print(f"   平均块大小: {len(full_content) / chunk_count:.1f} 字符/块")
            
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 流式测试异常: {e}")

def test_non_stream_comparison(message: str):
    """
    测试非流式响应作为对比
    
    @param message - 要发送的消息
    @returns 无返回值
    """
    print(f"\n📄 对比测试 - 非流式响应: {message}")
    print("=" * 80)
    
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
            content = data['choices'][0]['message']['content']
            
            print(f"⏱️ 总耗时: {end_time - start_time:.2f}秒")
            print(f"📝 响应内容长度: {len(content)} 字符")
            print("📄 完整响应:")
            print("-" * 40)
            print(content)
            print("-" * 40)
            
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 非流式测试异常: {e}")

def main():
    """
    主测试函数
    """
    print("🧪 RAG API 真正流式响应测试")
    print("=" * 80)
    
    # 测试问题列表
    test_questions = [
        "张三在哪个部门？",
        "技术部有哪些员工？",
        "Alpha项目的负责人是谁？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 测试 {i}/{len(test_questions)}")
        
        # 测试流式响应
        test_real_stream_chat(question)
        
        # 等待一下
        time.sleep(2)
        
        # 测试非流式响应作为对比
        test_non_stream_comparison(question)
        
        # 测试间隔
        if i < len(test_questions):
            print(f"\n⏳ 等待 3 秒后进行下一个测试...")
            time.sleep(3)
    
    print(f"\n✅ 所有测试完成！")
    print("💡 观察要点:")
    print("   1. 流式响应应该逐字符或逐词显示，而不是一次性显示")
    print("   2. 首个内容块延迟应该明显小于总耗时")
    print("   3. 内容块数量应该大于1（真正的流式）")

if __name__ == "__main__":
    main()
