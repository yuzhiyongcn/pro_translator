#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例脚本：演示如何使用DOCX到JSON转换器
"""

import os
import sys
from docx_to_json import DocxToJsonConverter


def demo_conversion():
    """Demo function to show how to use the converter"""
    
    print("DOCX到JSON转换器示例")
    print("=" * 40)
    
    # Look for docx files in the current directory and parent directory
    docx_files = []
    
    # Check current directory
    current_dir = os.getcwd()
    print(f"当前目录: {current_dir}")
    
    # Check parent directory for docx files
    parent_dir = os.path.dirname(current_dir)
    for file in os.listdir(parent_dir):
        if file.lower().endswith('.docx') and not file.startswith('~'):
            docx_files.append(os.path.join(parent_dir, file))
    
    if not docx_files:
        print("未找到DOCX文件")
        return
    
    print(f"找到 {len(docx_files)} 个DOCX文件:")
    for i, file in enumerate(docx_files, 1):
        print(f"{i}. {os.path.basename(file)}")
    
    # Let user choose a file or use the first one for demo
    try:
        choice = input(f"\n请选择文件编号 (1-{len(docx_files)}) 或按回车使用第一个文件: ").strip()
        
        if choice:
            file_index = int(choice) - 1
            if file_index < 0 or file_index >= len(docx_files):
                print("无效的文件编号")
                return
        else:
            file_index = 0
            
        selected_file = docx_files[file_index]
        print(f"\n选择的文件: {os.path.basename(selected_file)}")
        
    except ValueError:
        print("无效的输入")
        return
    except KeyboardInterrupt:
        print("\n用户取消操作")
        return
    
    # Create converter and process the file  
    converter = DocxToJsonConverter()
    
    # Generate output filename
    base_name = os.path.splitext(os.path.basename(selected_file))[0]
    output_file = f"{base_name}_fragments.json"
    
    print(f"\n开始处理文件...")
    print(f"输入文件: {selected_file}")
    print(f"输出文件: {output_file}")
    
    try:
        result = converter.convert_file(selected_file, output_file)
        
        if result:
            print(f"\n处理完成！")
            print(f"JSON文件已保存: {output_file}")
            
            # Show some sample fragments
            print(f"\n前10个文本片段示例:")
            sample_items = list(result.items())[:10]
            for i, (key, value) in enumerate(sample_items, 1):
                print(f"{i}. '{key}' : '{value}'")
            
            if len(result) > 10:
                print(f"... 还有 {len(result) - 10} 个片段")
                
        else:
            print("处理失败或未找到内容")
            
    except Exception as e:
        print(f"处理过程中发生错误: {e}")


if __name__ == "__main__":
    demo_conversion() 