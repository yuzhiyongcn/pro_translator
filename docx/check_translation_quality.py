#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查翻译质量
"""

import json
import re


def has_chinese(text):
    """Check if text contains Chinese characters"""
    if not text:
        return False
    return any('\u4e00' <= char <= '\u9fff' for char in text)


def count_chinese_chars(text):
    """Count Chinese characters in text"""
    if not text:
        return 0
    return len([char for char in text if '\u4e00' <= char <= '\u9fff'])


def main():
    filename = 'fully_translated_test_output_20250611植物提取物非临床安全性研究.json'
    
    print("翻译质量检查")
    print("=" * 50)
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"加载了 {len(data)} 个项目")
        
        # Check for Chinese characters
        items_with_chinese = []
        total_chinese_chars = 0
        
        for key, value in data.items():
            if has_chinese(value):
                chinese_count = count_chinese_chars(value)
                items_with_chinese.append((key, value, chinese_count))
                total_chinese_chars += chinese_count
        
        print(f"仍包含中文字符的项目: {len(items_with_chinese)}")
        print(f"总中文字符数: {total_chinese_chars}")
        
        if items_with_chinese:
            print("\n仍包含中文的项目:")
            for i, (key, value, count) in enumerate(items_with_chinese[:10]):
                print(f"{i+1}. 中文字符数: {count}")
                print(f"   键: {key[:50]}...")
                print(f"   值: {value[:100]}...")
                print()
        
        # Find long translated items to check quality
        long_items = [(k, v) for k, v in data.items() if len(v) > 80 and not has_chinese(v)]
        print(f"\n长文本翻译项目示例 (共{len(long_items)}个):")
        print("-" * 50)
        
        for i, (key, value) in enumerate(long_items[:5]):
            print(f"{i+1}. 原文: {key[:60]}...")
            print(f"   译文: {value[:80]}...")
            print()
        
        # Statistics
        print(f"\n=== 翻译统计 ===")
        print(f"总项目数: {len(data)}")
        print(f"完全翻译的项目: {len(data) - len(items_with_chinese)}")
        print(f"仍含中文的项目: {len(items_with_chinese)}")
        print(f"翻译成功率: {((len(data) - len(items_with_chinese)) / len(data) * 100):.1f}%")
        
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main() 