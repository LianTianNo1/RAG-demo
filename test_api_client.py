# -*- coding: utf-8 -*-
"""
RAG API客户端测试脚本

@remarks 用于测试RAG API服务的各种功能，包括文件上传、聊天对话等
@author AI Assistant
@version 1.0
"""

import requests
import json
import time
from pathlib import Path

# API服务器配置
API_BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def test_health_check():
    """
    测试健康检查接口
    
    @returns 无返回值
    """
    print("🔍 测试健康检查接口...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务状态: {data['status']}")
            print(f"📊 向量库就绪: {data['vector_store_ready']}")
            print(f"📁 知识库文件数: {data['knowledge_base_files']}")
            print(f"🕒 最后更新: {data.get('last_update', '未知')}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")

def test_file_upload(file_path: str):
    """
    测试文件上传接口
    
    @param file_path - 要上传的文件路径
    @returns 无返回值
    """
    print(f"📤 测试文件上传: {file_path}")
    try:
        if not Path(file_path).exists():
            print(f"❌ 文件不存在: {file_path}")
            return
        
        with open(file_path, "rb") as f:
            files = {"file": (Path(file_path).name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            response = requests.post(f"{API_BASE_URL}/v1/files/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 上传成功: {data['filename']}")
            print(f"📄 文件ID: {data['file_id']}")
            print(f"💬 消息: {data['message']}")
            print(f"🔐 文件哈希: {data['file_hash'][:16]}...")
        else:
            print(f"❌ 上传失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 上传异常: {e}")

def test_file_list():
    """
    测试文件列表接口
    
    @returns 无返回值
    """
    print("📋 测试文件列表接口...")
    try:
        response = requests.get(f"{API_BASE_URL}/v1/files/list")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 文件总数: {data['total_count']}")
            for file_info in data['files']:
                print(f"  📄 {file_info['filename']} ({file_info['size']} bytes)")
                print(f"     🕒 修改时间: {file_info['modified_time']}")
        else:
            print(f"❌ 获取文件列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取文件列表异常: {e}")

def test_chat_completion(message: str):
    """
    测试聊天完成接口
    
    @param message - 要发送的消息
    @returns 无返回值
    """
    print(f"💬 测试聊天接口: {message}")
    try:
        payload = {
            "model": "rag-excel",
            "messages": [
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(
            f"{API_BASE_URL}/v1/chat/completions",
            headers=HEADERS,
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            choice = data['choices'][0]
            message_content = choice['message']['content']
            
            print(f"✅ 响应ID: {data['id']}")
            print(f"🤖 助手回答:")
            print(f"   {message_content}")
            
            # 显示工具调用信息（如果有）
            if 'tool_calls' in choice['message']:
                print(f"🔧 工具调用:")
                for tool_call in choice['message']['tool_calls']:
                    func_name = tool_call['function']['name']
                    func_args = json.loads(tool_call['function']['arguments'])
                    print(f"   🛠️ {func_name}: {func_args}")
            
            # 显示使用统计
            usage = data['usage']
            print(f"📊 Token使用: 输入={usage['prompt_tokens']}, 输出={usage['completion_tokens']}, 总计={usage['total_tokens']}")
            
        else:
            print(f"❌ 聊天失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 聊天异常: {e}")

def test_vector_store_rebuild():
    """
    测试向量数据库重建接口
    
    @returns 无返回值
    """
    print("🔄 测试向量数据库重建...")
    try:
        response = requests.post(f"{API_BASE_URL}/v1/vector_store/rebuild")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 重建任务启动: {data['message']}")
        else:
            print(f"❌ 重建失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 重建异常: {e}")

def run_comprehensive_test():
    """
    运行综合测试
    
    @returns 无返回值
    """
    print("🚀 开始RAG API综合测试")
    print("=" * 50)
    
    # 1. 健康检查
    test_health_check()
    print()
    
    # 2. 文件列表
    test_file_list()
    print()
    
    # 3. 上传示例文件（如果存在）
    sample_file = "./data/sample_data.xlsx"
    if Path(sample_file).exists():
        test_file_upload(sample_file)
        print()
        
        # 等待一下让后台任务完成
        print("⏳ 等待向量数据库更新...")
        time.sleep(3)
        print()
    
    # 4. 测试聊天功能
    test_questions = [
        "你好，请介绍一下你的功能",
        "张三在哪个部门？",
        "Alpha项目的负责人是谁？",
        "技术部有哪些员工？",
        "请总结一下所有项目的情况"
    ]
    
    for question in test_questions:
        test_chat_completion(question)
        print()
        time.sleep(1)  # 避免请求过快
    
    # 5. 再次检查健康状态
    print("🔍 最终健康检查:")
    test_health_check()
    
    print("=" * 50)
    print("✅ RAG API综合测试完成")

if __name__ == "__main__":
    print("🧪 RAG API客户端测试工具")
    print("请确保API服务器正在运行 (python rag_api_server.py)")
    print()
    
    # 检查服务器是否可达
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            print("✅ API服务器连接成功")
            print()
            run_comprehensive_test()
        else:
            print(f"❌ API服务器响应异常: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"❌ 连接异常: {e}")
