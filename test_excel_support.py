#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Excel文件支持的脚本

@remarks 测试RAG系统是否正确支持 .xlsx 和 .xls 文件
@author AI Assistant
@version 1.0
"""

import os
import tempfile
from pathlib import Path
import pandas as pd

def create_test_excel_files():
    """
    创建测试用的Excel文件（.xlsx 和 .xls 格式）

    @returns 测试文件路径列表
    """
    test_files = []

    # 创建临时目录
    temp_dir = Path("./test_knowledge_base/")
    temp_dir.mkdir(exist_ok=True)

    # 测试数据
    test_data = {
        '姓名': ['张三', '李四', '王五'],
        '部门': ['技术部', '市场部', '人事部'],
        '薪资': [15000, 12000, 10000]
    }
    df = pd.DataFrame(test_data)

    # 创建 .xlsx 文件
    xlsx_file = temp_dir / "test_data.xlsx"
    df.to_excel(xlsx_file, index=False, engine='openpyxl')
    test_files.append(xlsx_file)
    print(f"创建了 .xlsx 文件: {xlsx_file}")

    # 创建一个假的 .xls 文件（只是为了测试glob模式）
    xls_file = temp_dir / "test_data.xls"
    with open(xls_file, 'w') as f:
        f.write("fake xls file for testing")
    test_files.append(xls_file)
    print(f"创建了 .xls 文件: {xls_file}")

    return test_files

def test_glob_patterns():
    """
    测试glob模式是否正确识别Excel文件

    @returns 测试结果
    """
    print("\n=== 测试glob模式 ===")

    # 创建测试文件
    test_files = create_test_excel_files()
    test_dir = Path("./test_knowledge_base/")

    # 测试错误的模式（原来的错误）
    print("\n1. 测试错误的glob模式:")
    try:
        wrong_pattern_files = list(test_dir.glob("*.xlsx,*.xls"))
        print(f"   错误模式 '*.xlsx,*.xls' 找到的文件: {len(wrong_pattern_files)}")
        for f in wrong_pattern_files:
            print(f"     - {f.name}")
    except Exception as e:
        print(f"   错误模式执行失败: {e}")

    # 测试正确的模式（修复后的方法）
    print("\n2. 测试正确的glob模式:")
    correct_files = []
    for pattern in ["*.xlsx", "*.xls"]:
        pattern_files = list(test_dir.glob(pattern))
        correct_files.extend(pattern_files)
        print(f"   模式 '{pattern}' 找到的文件: {len(pattern_files)}")
        for f in pattern_files:
            print(f"     - {f.name}")

    print(f"\n总共找到的Excel文件: {len(correct_files)}")

    # 清理测试文件
    for file in test_files:
        if file.exists():
            file.unlink()
    test_dir.rmdir()

    return len(correct_files) == 2

def test_rag_system_file_detection():
    """
    测试RAG系统的文件检测功能

    @returns 测试结果
    """
    print("\n=== 测试RAG系统文件检测 ===")

    try:
        # 导入RAG系统
        from rag_api_server import EnhancedRAGSystem

        # 创建测试文件
        test_files = create_test_excel_files()
        test_dir = Path("./test_knowledge_base/")

        # 创建RAG系统实例
        rag = EnhancedRAGSystem(
            knowledge_base_dir=str(test_dir),
            vector_store_dir="./test_vector_store/",
            embedding_model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            llm_model_name="qwen3:4b"
        )

        # 测试文件变化检测
        print("测试文件变化检测...")
        files_changed = rag.check_files_changed()
        print(f"检测到文件变化: {files_changed}")

        # 测试文档加载
        print("测试文档加载...")
        documents = rag._load_excel_documents()
        print(f"加载的文档数量: {len(documents)}")

        # 清理测试文件
        for file in test_files:
            if file.exists():
                file.unlink()
        test_dir.rmdir()

        # 清理向量存储目录
        vector_dir = Path("./test_vector_store/")
        if vector_dir.exists():
            import shutil
            shutil.rmtree(vector_dir)

        return len(documents) > 0

    except ImportError as e:
        print(f"无法导入RAG系统: {e}")
        return False
    except Exception as e:
        print(f"测试过程中出错: {e}")
        return False

if __name__ == "__main__":
    print("🧪 开始测试Excel文件支持...")

    # 检查依赖
    try:
        import pandas as pd
        import openpyxl
        print("✅ 所需依赖已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请安装: pip install pandas openpyxl")
        exit(1)

    # 运行测试
    test1_result = test_glob_patterns()
    test2_result = test_rag_system_file_detection()

    print("\n=== 测试结果 ===")
    print(f"Glob模式测试: {'✅ 通过' if test1_result else '❌ 失败'}")
    print(f"RAG系统测试: {'✅ 通过' if test2_result else '❌ 失败'}")

    if test1_result and test2_result:
        print("\n🎉 所有测试通过！Excel文件支持修复成功。")
    else:
        print("\n⚠️ 部分测试失败，请检查修复。")
