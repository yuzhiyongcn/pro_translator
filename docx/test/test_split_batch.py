#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分批翻译功能
"""

import os
import json
from json_translator_enhanced import EnhancedJsonTranslator


def create_test_data():
    """Create test data with different text lengths"""
    test_data = {
        "短文本1": "你好",
        "短文本2": "世界",
        "中等文本1": "这是一个中等长度的测试文本，包含了一些中文字符。",
        "中等文本2": "另一个中等长度的文本，用于测试翻译功能的稳定性。",
        "长文本1": "这是一个相对较长的测试文本，包含了更多的中文字符和标点符号。目的是测试翻译器在处理不同长度文本时的表现，特别是在批次分割时的字符平衡分配。",
        "长文本2": "第二个长文本示例，同样包含丰富的中文内容。这种长度的文本在实际应用中比较常见，需要确保翻译质量和批次处理的准确性。",
        "超长文本": "这是一个超长的测试文本，包含了大量的中文字符、标点符号和各种语言结构。目的是全面测试翻译器的批次分割算法，确保能够按照字符数量平均分配到不同的子批次中。在实际的文档翻译场景中，经常会遇到这种长度的文本段落，因此需要特别注意处理的准确性和效率。",
        "英文文本": "This is an English text that should remain unchanged.",
        "混合文本1": "这是一个Mixed文本，包含English和中文。",
        "混合文本2": "Another mixed text with中文和English content together."
    }
    return test_data


def test_split_batch_evenly():
    """Test the split_batch_evenly function"""
    print("=== 测试批次平均分割功能 ===")
    
    translator = EnhancedJsonTranslator()
    test_data = create_test_data()
    
    print(f"原始数据包含 {len(test_data)} 项:")
    for key, value in test_data.items():
        print(f"  {key}: {len(value)}字符 - '{value[:50]}{'...' if len(value) > 50 else ''}'")
    
    print(f"\n总字符数: {sum(len(v) for v in test_data.values())}")
    
    # Test splitting
    batch1, batch2 = translator.split_batch_evenly(test_data)
    
    print(f"\n=== 分割结果 ===")
    print(f"批次1 ({len(batch1)}项, {sum(len(v) for v in batch1.values())}字符):")
    for key, value in batch1.items():
        print(f"  {key}: {len(value)}字符")
    
    print(f"\n批次2 ({len(batch2)}项, {sum(len(v) for v in batch2.values())}字符):")
    for key, value in batch2.items():
        print(f"  {key}: {len(value)}字符")
    
    # Calculate balance
    chars1 = sum(len(v) for v in batch1.values())
    chars2 = sum(len(v) for v in batch2.values())
    total_chars = chars1 + chars2
    balance_ratio = abs(chars1 - chars2) / total_chars * 100
    
    print(f"\n=== 平衡度分析 ===")
    print(f"字符分布平衡度: {balance_ratio:.2f}% (差异越小越好)")
    print(f"项目分布: 批次1有{len(batch1)}项, 批次2有{len(batch2)}项")


def test_split_and_translate():
    """Test the complete split and translate functionality"""
    print("\n\n=== 测试分批翻译功能 ===")
    
    # Create a smaller test batch to avoid API costs
    test_batch = {
        "测试1": "你好，世界！",
        "测试2": "这是一个测试文本。",
        "测试3": "另一个中文测试。",
        "测试4": "第四个测试项目。"
    }
    
    translator = EnhancedJsonTranslator()
    
    print(f"测试批次包含 {len(test_batch)} 项:")
    for key, value in test_batch.items():
        print(f"  {key}: {value}")
    
    # Test the split and translate function
    print(f"\n开始测试分批翻译...")
    result = translator.split_and_translate_batch(test_batch)
    
    print(f"\n=== 翻译结果 ===")
    for key, value in result.items():
        original = test_batch[key]
        print(f"  {key}:")
        print(f"    原文: {original}")
        print(f"    译文: {value}")
        print(f"    仍含中文: {translator.has_chinese(value)}")


def main():
    """Main test function"""
    print("分批翻译功能测试")
    print("=" * 60)
    
    # Test 1: Split batch evenly
    test_split_batch_evenly()
    
    # Test 2: Split and translate (optional, requires API)
    user_input = input("\n是否测试实际翻译功能? (需要调用GPT API) [y/N]: ")
    if user_input.lower() in ['y', 'yes']:
        test_split_and_translate()
    else:
        print("跳过实际翻译测试")


if __name__ == "__main__":
    main() 