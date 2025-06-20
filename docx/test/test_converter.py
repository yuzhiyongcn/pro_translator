#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试DOCX到JSON转换器
"""

import os
import sys
from docx_to_json import DocxToJsonConverter


def test_converter():
    """Test the converter with available docx files"""
    
    print("测试DOCX到JSON转换器")
    print("=" * 40)
    
    # Look for docx files in current directory and parent directory
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    docx_files = []
    
    # Check current directory first
    try:
        for file in os.listdir(current_dir):
            if file.lower().endswith('.docx') and not file.startswith('~'):
                docx_files.append(os.path.join(current_dir, file))
    except:
        pass
    
    # Check parent directory if no files found in current
    if not docx_files:
        try:
            for file in os.listdir(parent_dir):
                if file.lower().endswith('.docx') and not file.startswith('~'):
                    docx_files.append(os.path.join(parent_dir, file))
        except:
            pass
    
    if not docx_files:
        print("未找到DOCX文件")
        return
    
    print(f"找到 {len(docx_files)} 个DOCX文件:")
    for i, file in enumerate(docx_files):
        print(f"{i+1}. {os.path.basename(file)}")
    
    # Test with the first file
    test_file = docx_files[2]
    print(f"\n测试文件: {os.path.basename(test_file)}")
    
    try:
        # Create converter
        converter = DocxToJsonConverter()
        
        # Process file
        output_file = f"test_output_{os.path.splitext(os.path.basename(test_file))[0]}.json"
        result = converter.convert_file(test_file, output_file)
        
        if result:
            print(f"\n✓ 转换成功!")
            print(f"✓ JSON文件已保存: {output_file}")
            print(f"✓ 处理的文本片段数量: {len(result)}")
            
            # Show first few fragments
            print(f"\n前5个文本片段示例:")
            sample_items = list(result.items())[:5]
            for i, (key, value) in enumerate(sample_items, 1):
                if len(key) > 50:
                    key_display = key[:47] + "..."
                else:
                    key_display = key
                print(f"{i}. '{key_display}'")
                
        else:
            print("✗ 转换失败")
            
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_converter() 