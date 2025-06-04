#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建示例Excel文件的脚本

@remarks 这个脚本用于生成示例Excel文件，包含员工信息和项目信息两个工作表
@author AI Assistant
@version 1.0
"""

import os
import csv

def create_sample_excel():
    """
    创建示例Excel文件，包含员工信息和项目信息

    @returns 无返回值
    @example
    ```python
    create_sample_excel()  # 在data目录下创建sample_data.xlsx
    ```
    """
    # 确保data目录存在
    data_dir = "./data/"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"创建了数据目录: {data_dir}")

    try:
        import pandas as pd

        # 创建示例数据
        # 员工信息表
        employees_data = pd.DataFrame({
            '姓名': ['张三', '李四', '王五', 'Alice'],
            '部门': ['技术部', '市场部', '技术部', '人事部'],
            '职位': ['软件工程师', '市场专员', '项目经理', 'HR专员'],
            '入职年份': [2020, 2021, 2019, 2022],
            '薪资(万)': [15, 12, 18, 10]
        })

        # 项目信息表
        projects_data = pd.DataFrame({
            '项目名称': ['Alpha项目', 'Beta项目', 'Gamma项目'],
            '负责人': ['王五', '张三', '李四'],
            '状态': ['进行中', '已完成', '规划中'],
            '预算(万)': [50, 30, 70],
            '开始时间': ['2023-01-15', '2022-06-01', '2023-03-01']
        })

        # 部门统计表
        department_stats = pd.DataFrame({
            '部门': ['技术部', '市场部', '人事部'],
            '人数': [2, 1, 1],
            '平均薪资(万)': [16.5, 12, 10],
            '部门预算(万)': [100, 50, 30]
        })

        # 创建Excel文件路径
        excel_file_path = os.path.join(data_dir, "sample_data.xlsx")

        # 使用ExcelWriter将多个DataFrame写入同一个Excel文件的不同工作表
        with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
            employees_data.to_excel(writer, sheet_name='员工信息', index=False)
            projects_data.to_excel(writer, sheet_name='项目信息', index=False)
            department_stats.to_excel(writer, sheet_name='部门统计', index=False)

        print(f"成功创建示例Excel文件: {excel_file_path}")
        print("文件包含以下工作表:")
        print("  - 员工信息: 包含员工的基本信息")
        print("  - 项目信息: 包含项目的详细信息")
        print("  - 部门统计: 包含各部门的统计数据")

        return excel_file_path

    except ImportError:
        print("pandas或openpyxl未安装，将创建CSV文件作为替代...")

        # 创建员工信息CSV
        employees_csv = os.path.join(data_dir, "employees.csv")
        with open(employees_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['姓名', '部门', '职位', '入职年份', '薪资(万)'])
            writer.writerow(['张三', '技术部', '软件工程师', '2020', '15'])
            writer.writerow(['李四', '市场部', '市场专员', '2021', '12'])
            writer.writerow(['王五', '技术部', '项目经理', '2019', '18'])
            writer.writerow(['Alice', '人事部', 'HR专员', '2022', '10'])

        # 创建项目信息CSV
        projects_csv = os.path.join(data_dir, "projects.csv")
        with open(projects_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['项目名称', '负责人', '状态', '预算(万)', '开始时间'])
            writer.writerow(['Alpha项目', '王五', '进行中', '50', '2023-01-15'])
            writer.writerow(['Beta项目', '张三', '已完成', '30', '2022-06-01'])
            writer.writerow(['Gamma项目', '李四', '规划中', '70', '2023-03-01'])

        print(f"已创建CSV文件:")
        print(f"  - {employees_csv}")
        print(f"  - {projects_csv}")
        print("注意：RAG系统需要Excel文件(.xlsx)，请手动将CSV转换为Excel格式，")
        print("或者安装pandas和openpyxl后重新运行此脚本。")

        return None

if __name__ == "__main__":
    create_sample_excel()
