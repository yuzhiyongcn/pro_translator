#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行增强版JSON翻译器
直接处理指定的JSON文件
"""

import os
from json_translator_enhanced import EnhancedJsonTranslator


def main():
    """Run enhanced translator on the specified file"""
    
    # Target file specified by user (in parent directory)
    target_file = "../translated_test_output_20250611植物提取物非临床安全性研究.json"
    
    print("增强版JSON翻译器")
    print("=" * 50)
    print(f"目标文件: {target_file}")
    
    # Check if file exists
    if not os.path.exists(target_file):
        print(f"错误: 目标文件不存在: {target_file}")
        print("请确保文件在当前目录中")
        return
    
    # Create enhanced translator
    translator = EnhancedJsonTranslator()
    
    # Set output filename
    output_file = f"fully_translated_test_output_20250611植物提取物非临床安全性研究.json"
    
    print(f"输出文件: {output_file}")
    print("\n开始强力翻译...")
    
    # Run translation
    success = translator.translate_json_file(target_file, output_file)
    
    if success:
        print(f"\n🎉 翻译成功完成！")
        print(f"📁 输出文件: {output_file}")
        print(f"\n建议检查输出文件中的翻译质量")
    else:
        print(f"\n❌ 翻译失败")


if __name__ == "__main__":
    main() 