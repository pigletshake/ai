#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取demo.json文件中的数据脚本
提取字段：id, question, ip, created_at, answer, type
"""

import json
import sys
from typing import List, Dict, Any

def extract_data_from_json(file_path: str) -> List[Dict[str, Any]]:
    """
    从JSON文件中提取指定字段的数据
    字段顺序：id, question, answer, created_at, ip, type, subtype
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        包含提取数据的列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"错误：JSON解析失败 - {e}")
        return []
    
    extracted_data = []
    
    for item in data:
        try:
            # 按指定顺序提取字段
            record = {
                'id': item.get('id', ''),
                'question': '',
                'answer': item.get('answer', ''),
                'created_at': item.get('created_at', ''),
                'ip': item.get('ip', ''),
                'type': '',
                'subtype': ''
            }
            
            # 解析arg1字段中的JSON
            arg1_str = item.get('arg1', '')
            if arg1_str:
                try:
                    # 尝试修复不完整的JSON
                    fixed_arg1 = arg1_str
                    # 如果JSON不完整，尝试修复
                    if not arg1_str.endswith('}'):
                        # 查找最后一个完整的字段
                        if '"sub"' in arg1_str and not '"subtype"' in arg1_str:
                            fixed_arg1 = arg1_str.replace('"sub"}', '"subtype": ""}')
                        elif '"subtype": "' in arg1_str and not arg1_str.endswith('"}'):
                            fixed_arg1 = arg1_str + '"}'
                    
                    arg1_data = json.loads(fixed_arg1)
                    record['question'] = arg1_data.get('question', '')
                    record['type'] = arg1_data.get('type', '')
                    # 提取subtype字段（可能是subtype或subt）
                    record['subtype'] = arg1_data.get('subtype', '') or arg1_data.get('subt', '')
                except json.JSONDecodeError:
                    # 如果JSON解析失败，尝试正则表达式提取
                    import re
                    question_match = re.search(r'"question":\s*"([^"]*)"', arg1_str)
                    type_match = re.search(r'"type":\s*"([^"]*)"', arg1_str)
                    subtype_match = re.search(r'"subtype":\s*"([^"]*)"', arg1_str) or re.search(r'"sub":\s*"([^"]*)"', arg1_str)
                    
                    record['question'] = question_match.group(1) if question_match else ''
                    record['type'] = type_match.group(1) if type_match else ''
                    record['subtype'] = subtype_match.group(1) if subtype_match else ''
            else:
                record['question'] = ''
                record['type'] = ''
                record['subtype'] = ''
            
            extracted_data.append(record)
            
        except Exception as e:
            print(f"警告：处理记录时出错 - {e}")
            continue
    
    return extracted_data

def save_to_csv(data: List[Dict[str, Any]], output_file: str = 'extracted_data1.csv'):
    """
    将提取的数据保存为CSV文件
    
    Args:
        data: 提取的数据列表
        output_file: 输出CSV文件名
    """
    import csv
    
    if not data:
        print("没有数据可保存")
        return
    
    fieldnames = ['id', 'question', 'answer', 'created_at', 'ip', 'type', 'subtype']
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"数据已保存到 {output_file}")
    except Exception as e:
        print(f"保存CSV文件时出错：{e}")

def print_data(data: List[Dict[str, Any]], limit: int = 10):
    """
    打印提取的数据（限制显示数量）
    
    Args:
        data: 提取的数据列表
        limit: 显示的最大记录数
    """
    if not data:
        print("没有数据可显示")
        return
    
    print(f"\n提取的数据（显示前{min(limit, len(data))}条）：")
    print("-" * 100)
    
    for i, record in enumerate(data[:limit]):
        print(f"记录 {i+1}:")
        print(f"  ID: {record['id']}")
        print(f"  提问: {record['question']}")
        print(f"  答案: {record['answer'][:100]}{'...' if len(record['answer']) > 100 else ''}")
        print(f"  日期: {record['created_at']}")
        print(f"  IP: {record['ip']}")
        print(f"  类型1: {record['type']}")
        print(f"  类型2: {record['subtype']}")
        print("-" * 100)

def main():
    """主函数"""
    input_file = 'demo.json'
    
    print("开始提取demo.json文件中的数据...")
    
    # 提取数据
    extracted_data = extract_data_from_json(input_file)
    
    if not extracted_data:
        print("没有提取到任何数据")
        return
    
    print(f"成功提取 {len(extracted_data)} 条记录")
    
    # 显示部分数据
    print_data(extracted_data, limit=5)
    
    # 保存为CSV文件
    save_to_csv(extracted_data, 'extracted_data3.csv')
    
    # 显示统计信息
    print(f"\n统计信息：")
    print(f"总记录数: {len(extracted_data)}")
    
    # 统计有问题的记录数
    with_questions = sum(1 for record in extracted_data if record['question'].strip())
    print(f"有问题的记录数: {with_questions}")
    
    # 统计类型分布
    type_counts = {}
    subtype_counts = {}
    for record in extracted_data:
        type_val = record['type']
        subtype_val = record['subtype']
        type_counts[type_val] = type_counts.get(type_val, 0) + 1
        subtype_counts[subtype_val] = subtype_counts.get(subtype_val, 0) + 1
    
    print(f"类型1分布:")
    for type_val, count in sorted(type_counts.items()):
        print(f"  {type_val}: {count}")
    
    print(f"类型2分布:")
    for subtype_val, count in sorted(subtype_counts.items()):
        print(f"  {subtype_val}: {count}")

if __name__ == "__main__":
    main()

