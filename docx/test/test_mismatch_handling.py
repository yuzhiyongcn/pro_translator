#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试翻译前后数量不匹配的处理逻辑
"""

import json
from json_translator_enhanced import EnhancedJsonTranslator


class MockGPTWrapper:
    """Mock GPT wrapper for testing mismatch scenarios"""
    
    def __init__(self, behavior="normal"):
        self.behavior = behavior
        self.call_count = 0
    
    def query(self, text):
        """Mock query method that simulates different behaviors"""
        self.call_count += 1
        
        if self.behavior == "missing_items":
            # Simulate missing items in response
            items = text.split("[#]")
            # Return fewer items than input
            return "[#]".join(items[:-1])  # Drop last item
            
        elif self.behavior == "extra_items":
            # Simulate extra items in response
            items = text.split("[#]")
            return "[#]".join(items + ["Extra item"])  # Add extra item
            
        elif self.behavior == "severe_mismatch":
            # Simulate severe mismatch (difference > 1)
            items = text.split("[#]")
            if len(items) > 3:
                return "[#]".join(items[:len(items)//2])  # Return only half
            else:
                return "[#]".join(items)
                
        else:  # normal behavior
            # Normal behavior - just echo back with "translated" prefix
            items = text.split("[#]")
            translated = ["[Translated] " + item for item in items]
            return "[#]".join(translated)


def test_normal_translation():
    """Test normal translation (no mismatch)"""
    print("=== 测试正常翻译（无数量不匹配） ===")
    
    translator = EnhancedJsonTranslator()
    translator.gpt = MockGPTWrapper("normal")
    
    test_batch = {
        "key1": "文本1",
        "key2": "文本2", 
        "key3": "文本3"
    }
    
    print(f"输入批次: {len(test_batch)} 项")
    result = translator.translate_batch(test_batch)
    print(f"输出结果: {len(result)} 项")
    
    print("结果对比:")
    for key in test_batch:
        print(f"  {key}: '{test_batch[key]}' -> '{result.get(key, 'MISSING')}'")


def test_minor_mismatch():
    """Test minor mismatch (difference = 1)"""
    print("\n=== 测试轻微不匹配（差异=1） ===")
    
    translator = EnhancedJsonTranslator()
    translator.gpt = MockGPTWrapper("missing_items")
    
    test_batch = {
        "key1": "文本1",
        "key2": "文本2",
        "key3": "文本3"
    }
    
    print(f"输入批次: {len(test_batch)} 项")
    result = translator.translate_batch(test_batch)
    print(f"输出结果: {len(result)} 项")
    
    print("结果对比:")
    for key in test_batch:
        print(f"  {key}: '{test_batch[key]}' -> '{result.get(key, 'MISSING')}'")


def test_severe_mismatch():
    """Test severe mismatch (difference > 1)"""
    print("\n=== 测试严重不匹配（差异>1，触发分批） ===")
    
    translator = EnhancedJsonTranslator()
    translator.gpt = MockGPTWrapper("severe_mismatch")
    
    test_batch = {
        "key1": "文本1",
        "key2": "文本2",
        "key3": "文本3",
        "key4": "文本4",
        "key5": "文本5"
    }
    
    print(f"输入批次: {len(test_batch)} 项")
    print("预期：触发分批处理")
    
    result = translator.translate_batch(test_batch)
    print(f"输出结果: {len(result)} 项")
    
    print("结果对比:")
    for key in test_batch:
        print(f"  {key}: '{test_batch[key]}' -> '{result.get(key, 'MISSING')}'")


def test_split_functionality():
    """Test the split functionality specifically"""
    print("\n=== 测试分批功能 ===")
    
    translator = EnhancedJsonTranslator()
    
    # Test different batch sizes
    test_cases = [
        {"key1": "短文本"},
        {"key1": "文本1", "key2": "文本2"},
        {"key1": "长文本1"*10, "key2": "长文本2"*10, "key3": "短文本", "key4": "中等文本"*5},
        {"key1": "超长文本"*20, "key2": "短", "key3": "中等文本"*3, "key4": "另一个长文本"*15, "key5": "短文本"}
    ]
    
    for i, batch in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {len(batch)} 项")
        
        total_chars = sum(len(v) for v in batch.values())
        print(f"总字符数: {total_chars}")
        
        if len(batch) <= 1:
            print("批次太小，无法分割")
            continue
            
        batch1, batch2 = translator.split_batch_evenly(batch)
        
        chars1 = sum(len(v) for v in batch1.values())
        chars2 = sum(len(v) for v in batch2.values())
        
        print(f"分割结果: 批次1({len(batch1)}项, {chars1}字符) + 批次2({len(batch2)}项, {chars2}字符)")
        
        if total_chars > 0:
            balance = abs(chars1 - chars2) / total_chars * 100
            print(f"平衡度: {balance:.2f}%")


def test_recursive_splitting():
    """Test recursive splitting behavior"""
    print("\n=== 测试递归分批行为 ===")
    
    # Create a translator that always reports severe mismatch on first try
    class TestTranslator(EnhancedJsonTranslator):
        def __init__(self):
            super().__init__()
            self.split_attempts = 0
        
        def translate_batch(self, batch, attempt=1):
            # Only trigger split on first attempt for each batch
            if attempt == 1 and len(batch) > 2 and self.split_attempts < 1:
                self.split_attempts += 1
                print(f"模拟严重不匹配，触发分批 (批次大小: {len(batch)})")
                return self.split_and_translate_batch(batch, attempt)
            else:
                # Normal processing for smaller batches
                print(f"正常处理批次 (大小: {len(batch)})")
                return {k: f"[已翻译] {v}" for k, v in batch.items()}
    
    translator = TestTranslator()
    
    test_batch = {
        "key1": "测试文本1",
        "key2": "测试文本2", 
        "key3": "测试文本3",
        "key4": "测试文本4",
        "key5": "测试文本5"
    }
    
    print(f"测试递归分批: {len(test_batch)} 项")
    result = translator.translate_batch(test_batch)
    
    print(f"最终结果: {len(result)} 项")
    for key, value in result.items():
        print(f"  {key}: {value}")


def main():
    """Main test function"""
    print("翻译数量不匹配处理逻辑测试")
    print("=" * 60)
    
    # Test different scenarios
    test_normal_translation()
    test_minor_mismatch()
    test_severe_mismatch()
    test_split_functionality()
    test_recursive_splitting()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    
    print("\n💡 关键改进点:")
    print("1. 轻微不匹配(差异≤1): 智能映射，保留原文作为后备")
    print("2. 严重不匹配(差异>1): 自动分为两个较小批次重新翻译")
    print("3. 分批算法: 按字符数量平衡分配，确保负载均衡")
    print("4. 递归处理: 支持多层分批，直到成功或无法再分")


if __name__ == "__main__":
    main() 