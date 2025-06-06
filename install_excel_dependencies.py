#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装Excel文件支持所需的依赖

@remarks 自动安装支持 .xlsx 和 .xls 文件所需的Python包
@author AI Assistant
@version 1.0
"""

import subprocess
import sys

def install_package(package_name):
    """
    安装Python包
    
    @param package_name - 包名
    @returns 安装是否成功
    """
    try:
        print(f"正在安装 {package_name}...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package_name
        ], capture_output=True, text=True, check=True)
        print(f"✅ {package_name} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package_name} 安装失败:")
        print(f"   错误信息: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ 安装 {package_name} 时发生未知错误: {e}")
        return False

def check_package(package_name):
    """
    检查包是否已安装
    
    @param package_name - 包名
    @returns 是否已安装
    """
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def main():
    """
    主函数：检查并安装Excel支持所需的依赖
    """
    print("🔧 检查Excel文件支持依赖...")
    
    # 需要安装的包列表
    required_packages = [
        ("pandas", "pandas"),           # 数据处理
        ("openpyxl", "openpyxl"),      # .xlsx 文件支持
        ("xlrd", "xlrd"),              # .xls 文件支持
    ]
    
    installed_packages = []
    failed_packages = []
    
    for import_name, package_name in required_packages:
        print(f"\n检查 {package_name}...")
        
        if check_package(import_name):
            print(f"✅ {package_name} 已安装")
            installed_packages.append(package_name)
        else:
            print(f"⚠️ {package_name} 未安装，正在安装...")
            if install_package(package_name):
                installed_packages.append(package_name)
            else:
                failed_packages.append(package_name)
    
    # 输出结果
    print("\n" + "="*50)
    print("📊 安装结果:")
    print(f"✅ 成功安装/已存在: {len(installed_packages)} 个包")
    for pkg in installed_packages:
        print(f"   - {pkg}")
    
    if failed_packages:
        print(f"❌ 安装失败: {len(failed_packages)} 个包")
        for pkg in failed_packages:
            print(f"   - {pkg}")
        print("\n⚠️ 部分依赖安装失败，可能影响 .xls 文件的读取功能")
        print("请手动运行以下命令:")
        for pkg in failed_packages:
            print(f"   pip install {pkg}")
    else:
        print("\n🎉 所有依赖安装完成！现在可以正常处理 .xlsx 和 .xls 文件了")
    
    # 测试导入
    print("\n🧪 测试依赖导入...")
    try:
        import pandas as pd
        print("✅ pandas 导入成功")
        
        import openpyxl
        print("✅ openpyxl 导入成功")
        
        import xlrd
        print("✅ xlrd 导入成功")
        
        print("\n✨ 所有依赖测试通过！")
        
    except ImportError as e:
        print(f"❌ 导入测试失败: {e}")
        print("请检查安装是否成功")

if __name__ == "__main__":
    main()
