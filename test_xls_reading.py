#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 .xls 文件读取功能

@remarks 验证修复后的系统是否能正确读取 .xls 文件
@author AI Assistant
@version 1.0
"""

import pandas as pd
from pathlib import Path

def test_xls_file_reading():
    """
    测试读取知识库中的 .xls 文件
    """
    print("🧪 测试 .xls 文件读取功能...")
    
    knowledge_base_dir = Path("./knowledge_base/")
    
    if not knowledge_base_dir.exists():
        print("❌ 知识库目录不存在")
        return False
    
    # 查找所有 .xls 文件
    xls_files = list(knowledge_base_dir.glob("*.xls"))
    
    if not xls_files:
        print("⚠️ 知识库中没有找到 .xls 文件")
        return True
    
    print(f"📁 找到 {len(xls_files)} 个 .xls 文件:")
    for file in xls_files:
        print(f"   - {file.name}")
    
    # 测试读取每个文件
    success_count = 0
    for file_path in xls_files:
        print(f"\n📖 正在测试读取: {file_path.name}")
        try:
            # 尝试使用 xlrd 引擎读取
            xls = pd.read_excel(file_path, sheet_name=None, engine='xlrd')
            print(f"   ✅ 成功读取，包含 {len(xls)} 个工作表:")
            
            for sheet_name, df in xls.items():
                print(f"      - 工作表 '{sheet_name}': {df.shape[0]} 行 x {df.shape[1]} 列")
                if not df.empty:
                    print(f"        列名: {list(df.columns)[:5]}{'...' if len(df.columns) > 5 else ''}")
            
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ 读取失败: {e}")
            
            # 尝试其他方法
            try:
                print("   🔄 尝试使用默认引擎...")
                xls = pd.read_excel(file_path, sheet_name=None)
                print(f"   ✅ 使用默认引擎成功读取")
                success_count += 1
            except Exception as e2:
                print(f"   ❌ 默认引擎也失败: {e2}")
    
    print(f"\n📊 测试结果: {success_count}/{len(xls_files)} 个文件读取成功")
    return success_count == len(xls_files)

def test_rag_system_with_xls():
    """
    测试RAG系统处理 .xls 文件
    """
    print("\n🤖 测试RAG系统处理 .xls 文件...")
    
    try:
        from rag_api_server import EnhancedRAGSystem
        
        # 创建RAG系统实例
        rag = EnhancedRAGSystem(
            knowledge_base_dir="./knowledge_base/",
            vector_store_dir="./vector_store/",
            embedding_model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            llm_model_name="qwen3:4b"
        )
        
        print("📚 测试文档加载...")
        documents = rag._load_excel_documents()
        
        # 统计不同类型文件的文档数量
        xlsx_docs = 0
        xls_docs = 0
        
        for doc in documents:
            source_file = doc.metadata.get("source_file", "")
            if source_file.endswith('.xlsx'):
                xlsx_docs += 1
            elif source_file.endswith('.xls'):
                xls_docs += 1
        
        print(f"📊 文档加载结果:")
        print(f"   - 总文档数: {len(documents)}")
        print(f"   - .xlsx 文件文档: {xlsx_docs}")
        print(f"   - .xls 文件文档: {xls_docs}")
        
        if xls_docs > 0:
            print("✅ RAG系统成功处理了 .xls 文件")
            return True
        else:
            print("⚠️ RAG系统没有处理到 .xls 文件")
            return False
            
    except Exception as e:
        print(f"❌ RAG系统测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🔍 开始测试 .xls 文件支持...")
    
    # 测试1: 直接读取 .xls 文件
    test1_result = test_xls_file_reading()
    
    # 测试2: RAG系统处理 .xls 文件
    test2_result = test_rag_system_with_xls()
    
    print("\n" + "="*50)
    print("📋 最终测试结果:")
    print(f"   直接读取测试: {'✅ 通过' if test1_result else '❌ 失败'}")
    print(f"   RAG系统测试: {'✅ 通过' if test2_result else '❌ 失败'}")
    
    if test1_result and test2_result:
        print("\n🎉 .xls 文件支持测试全部通过！")
        print("现在可以正常处理 .xlsx 和 .xls 两种格式的Excel文件了。")
    else:
        print("\n⚠️ 部分测试失败，请检查配置。")
