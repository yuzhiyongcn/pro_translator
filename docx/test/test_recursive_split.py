#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试递归分割到单个元素的行为
"""

from json_translator_enhanced import EnhancedJsonTranslator


class AlwaysMismatchGPT:
    """模拟总是产生数量不匹配的GPT"""
    
    def __init__(self):
        self.call_count = 0
        
    def query(self, text):
        self.call_count += 1
        items = text.split("[#]")
        
        # 总是返回比输入少的项目，触发数量不匹配
        if len(items) > 2:
            print(f"  GPT调用{self.call_count}: 输入{len(items)}项，返回{len(items)//2}项 (模拟严重不匹配)")
            return "[#]".join(items[:len(items)//2])  # 返回一半的项目，差异>1
        elif len(items) == 2:
            print(f"  GPT调用{self.call_count}: 输入{len(items)}项，返回0项 (模拟严重不匹配)")
            return ""  # 返回空，差异=2>1
        else:
            print(f"  GPT调用{self.call_count}: 输入{len(items)}项，正常返回{len(items)}项")
            return f"[已翻译] {text}"


def test_recursive_split_to_single():
    """测试递归分割到单个元素"""
    print("=== 测试递归分割到单个元素 ===")
    
    translator = EnhancedJsonTranslator()
    translator.gpt = AlwaysMismatchGPT()
    
    # 创建一个包含多个元素的测试批次
    test_batch = {
        "item1": "测试文本1",
        "item2": "测试文本2", 
        "item3": "测试文本3",
        "item4": "测试文本4",
        "item5": "测试文本5",
        "item6": "测试文本6",
        "item7": "测试文本7",
        "item8": "测试文本8"
    }
    
    print(f"初始批次: {len(test_batch)} 项")
    for key, value in test_batch.items():
        print(f"  {key}: {value}")
    
    print(f"\n开始翻译（预期：递归分割到单个元素）...")
    print("=" * 50)
    
    result = translator.translate_batch(test_batch)
    
    print("=" * 50)
    print(f"最终结果: {len(result)} 项")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    print(f"\nGPT总调用次数: {translator.gpt.call_count}")


def analyze_split_behavior():
    """分析分割行为的边界条件"""
    print("\n=== 分析分割行为的边界条件 ===")
    
    translator = EnhancedJsonTranslator()
    
    # 测试不同大小的批次分割
    test_cases = [
        {"single": "单个项目"},
        {"item1": "项目1", "item2": "项目2"},
        {"item1": "项目1", "item2": "项目2", "item3": "项目3"},
        {"item1": "项目1", "item2": "项目2", "item3": "项目3", "item4": "项目4"}
    ]
    
    for i, batch in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {len(batch)} 项")
        
        if len(batch) <= 1:
            print("  ≤1项: 无法分割，直接返回")
            continue
            
        if len(batch) <= 2:
            print("  ≤2项: 特殊处理")
            batch1, batch2 = translator.split_batch_evenly(batch)
            print(f"    分割结果: batch1={len(batch1)}项, batch2={len(batch2)}项")
            
            if len(batch) == 1:
                print("    1项 -> (1项, 0项)")
            else:
                print("    2项 -> (1项, 1项)")
        else:
            print("  >2项: 正常分割")
            batch1, batch2 = translator.split_batch_evenly(batch)
            print(f"    分割结果: batch1={len(batch1)}项, batch2={len(batch2)}项")


def trace_recursive_calls():
    """追踪递归调用过程"""
    print("\n=== 追踪递归调用过程 ===")
    
    class TracingTranslator(EnhancedJsonTranslator):
        def __init__(self):
            super().__init__()
            self.call_depth = 0
            self.gpt = AlwaysMismatchGPT()
        
        def translate_batch(self, batch, attempt=1):
            self.call_depth += 1
            indent = "  " * self.call_depth
            print(f"{indent}├─ translate_batch: {len(batch)}项 (深度{self.call_depth})")
            
            result = super().translate_batch(batch, attempt)
            
            self.call_depth -= 1
            return result
        
        def split_and_translate_batch(self, batch, attempt=1):
            self.call_depth += 1
            indent = "  " * self.call_depth
            print(f"{indent}├─ split_and_translate_batch: {len(batch)}项 (深度{self.call_depth})")
            
            result = super().split_and_translate_batch(batch, attempt)
            
            self.call_depth -= 1
            return result
    
    translator = TracingTranslator()
    
    test_batch = {
        "a": "文本A",
        "b": "文本B", 
        "c": "文本C",
        "d": "文本D",
        "e": "文本E"
    }
    
    print(f"开始追踪 {len(test_batch)} 项批次的递归调用:")
    print("调用树:")
    
    result = translator.translate_batch(test_batch)
    
    print(f"\n追踪完成，最终得到 {len(result)} 项结果")


def main():
    """主测试函数"""
    print("递归分割到单个元素的行为测试")
    print("=" * 60)
    
    # 分析边界条件
    analyze_split_behavior()
    
    # 追踪递归调用
    trace_recursive_calls()
    
    # 测试完整的递归分割
    test_recursive_split_to_single()
    
    print("\n" + "=" * 60)
    print("📋 分析结论:")
    print("1. 批次≤1项: 无法分割，直接返回原批次")
    print("2. 批次=2项: 分割为(1项, 1项)")
    print("3. 批次>2项: 按字符数平衡分割")
    print("4. 递归终止条件: 当子批次≤1项时停止分割")
    print("5. 最终结果: 理论上可以分割到每个批次只有1项")


if __name__ == "__main__":
    main() 