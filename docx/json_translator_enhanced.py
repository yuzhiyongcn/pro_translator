#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版JSON翻译器
使用GPT-4o-mini强力翻译JSON文件中的所有中文内容到英文
采用多轮迭代，确保所有中文都被翻译
"""

import os
import sys
import json
import re
import time
import math
from typing import Dict, List, Tuple

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gpt_wrapper import GPTWrapper
import string_utils as su


class EnhancedJsonTranslator:
    def __init__(self, model="gpt-4o-mini"):
        """Initialize the enhanced JSON translator"""
        self.model = model
        self.gpt = GPTWrapper(model=model)
        self.max_tokens_per_batch = 1500  # More conservative limit
        self.separator = "[#]"
        self.max_retries = 10  # Increased retry limit
        
        # Set up system prompt for translation
        system_prompt = """You are a professional Chinese to English translator with expertise in medical and scientific terminology.

CRITICAL RULES:
1. Translate ALL Chinese characters to English - leave NO Chinese characters untranslated
2. Keep English letters, numbers, symbols, punctuation, and abbreviations exactly as they are
3. Preserve all spacing, line breaks, and formatting exactly
4. For mixed Chinese-English text, translate only the Chinese parts
5. Do not add explanations, notes, or extra content
6. Return ONLY the translated text

Input format: Multiple text fragments separated by '[#]'
Output format: Translated fragments separated by '[#]' in EXACT same order

EXAMPLES:
Input: "测试文本[#]Hello World[#]数字123保持不变[#]中英mixed文本[#]English text"
Output: "test text[#]Hello World[#]number 123 remains unchanged[#]Chinese-English mixed text[#]English text"

Input: "方法学验证符合2020版药典要求[#]Test with 数字456[#]纯英文text"
Output: "methodological verification complies with 2020 Pharmacopoeia requirements[#]Test with number 456[#]纯英文text"

TRANSLATE EVERYTHING CHINESE. NO EXCEPTIONS.
"""
        self.gpt.set_system_prompt(system_prompt)
    
    def has_chinese(self, text: str) -> bool:
        """Check if text contains Chinese characters"""
        if not text:
            return False
        return any('\u4e00' <= char <= '\u9fff' for char in text)
    
    def count_chinese_chars(self, text: str) -> int:
        """Count Chinese characters in text"""
        if not text:
            return 0
        return len([char for char in text if '\u4e00' <= char <= '\u9fff'])
    
    def extract_chinese_items(self, items: Dict[str, str]) -> Dict[str, str]:
        """Extract items that contain Chinese characters"""
        chinese_items = {}
        for key, value in items.items():
            if self.has_chinese(value):
                chinese_items[key] = value
        return chinese_items
    
    def estimate_token_count(self, text: str) -> int:
        """Estimate token count for a text string"""
        # More conservative estimation for mixed Chinese/English text
        return len(text) // 2
    
    def create_small_batches(self, items: Dict[str, str]) -> List[Dict[str, str]]:
        """Create smaller batches to improve translation quality"""
        batches = []
        current_batch = {}
        current_token_count = 0
        
        # Sort items by length to better group them
        sorted_items = sorted(items.items(), key=lambda x: len(x[1]))
        
        for key, value in sorted_items:
            estimated_tokens = self.estimate_token_count(value)
            
            # Use smaller batches for better quality
            if current_token_count + estimated_tokens > self.max_tokens_per_batch and current_batch:
                batches.append(current_batch)
                current_batch = {}
                current_token_count = 0
            
            current_batch[key] = value
            current_token_count += estimated_tokens
        
        # Add the last batch if it has items
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    def translate_batch(self, batch: Dict[str, str], attempt: int = 1) -> Dict[str, str]:
        """Translate a batch of items with enhanced error handling"""
        if not batch:
            return {}
        
        # Create input text with separator
        keys = list(batch.keys())
        values = list(batch.values())
        input_text = self.separator.join(values)
        
        try:
            print(f"正在翻译批次，包含 {len(batch)} 个项目 (尝试 {attempt})...")
            print(f"输入文本长度: {len(input_text)} 字符")
            
            total_chinese_chars = sum(self.count_chinese_chars(v) for v in values)
            print(f"待翻译中文字符数: {total_chinese_chars}")
            
            # Call GPT for translation with retry
            max_attempts = 3
            for retry in range(max_attempts):
                try:
                    translated_text = self.gpt.query(input_text)
                    break
                except Exception as e:
                    print(f"API调用失败 (重试 {retry + 1}/{max_attempts}): {e}")
                    if retry < max_attempts - 1:
                        time.sleep(2 ** retry)  # Exponential backoff
                    else:
                        raise
            
            # Split the translated text
            translated_values = translated_text.split(self.separator)
            
            # Verify the count matches
            if len(translated_values) != len(values):
                print(f"警告: 翻译前后数量不匹配！")
                print(f"原始数量: {len(values)}, 翻译后数量: {len(translated_values)}")
                
                # If counts don't match severely, split into smaller batches
                if abs(len(translated_values) - len(values)) > 1:
                    print("数量差异过大，将批次分为两个较小批次")
                    return self.split_and_translate_batch(batch, attempt)
            
            # Create result dictionary
            result = {}
            for i, key in enumerate(keys):
                if i < len(translated_values):
                    result[key] = translated_values[i].strip()
                else:
                    result[key] = values[i]  # Keep original if no translation
            
            # Check translation quality
            result_chinese_chars = sum(self.count_chinese_chars(v) for v in result.values())
            print(f"翻译后剩余中文字符数: {result_chinese_chars}")
            
            return result
            
        except Exception as e:
            print(f"翻译批次时发生错误: {e}")
            return batch
    
    def split_batch_evenly(self, batch: Dict[str, str]) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Split a batch into two smaller batches, balanced by character count"""
        if len(batch) <= 2:
            # Cannot split further effectively, return as two separate batches
            items = list(batch.items())
            if len(items) == 1:
                return {items[0][0]: items[0][1]}, {}
            else:
                return {items[0][0]: items[0][1]}, {items[1][0]: items[1][1]}
        
        # Sort items by character length for better distribution
        items = list(batch.items())
        items.sort(key=lambda x: len(x[1]), reverse=True)
        
        # Split items trying to balance character count
        batch1 = {}
        batch2 = {}
        batch1_chars = 0
        batch2_chars = 0
        
        # Use greedy algorithm to balance character counts
        for key, value in items:
            char_count = len(value)
            if batch1_chars <= batch2_chars:
                batch1[key] = value
                batch1_chars += char_count
            else:
                batch2[key] = value
                batch2_chars += char_count
        
        print(f"分批结果: 批次1有{len(batch1)}项({batch1_chars}字符), 批次2有{len(batch2)}项({batch2_chars}字符)")
        return batch1, batch2
    
    def split_and_translate_batch(self, batch: Dict[str, str], attempt: int = 1) -> Dict[str, str]:
        """Split batch into two smaller batches and translate each separately"""
        if len(batch) <= 1:
            # Cannot split single item, return as-is for further processing
            print("批次只有1项，无法进一步分割")
            return batch
        
        print(f"将包含{len(batch)}项的批次分为两个较小批次...")
        
        # Split the batch into two smaller batches
        batch1, batch2 = self.split_batch_evenly(batch)
        
        result = {}
        
        # Translate first batch
        if batch1:
            print(f"翻译第1个子批次({len(batch1)}项)...")
            result1 = self.translate_batch(batch1, attempt)
            result.update(result1)
            
            # Small delay between sub-batches
            time.sleep(0.5)
        
        # Translate second batch
        if batch2:
            print(f"翻译第2个子批次({len(batch2)}项)...")
            result2 = self.translate_batch(batch2, attempt)
            result.update(result2)
        
        print(f"子批次翻译完成，总共处理了{len(result)}项")
        return result
    
    def validate_translation(self, items: Dict[str, str]) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Validate translation results with detailed analysis
        Returns: (successfully_translated, still_has_chinese)
        """
        successfully_translated = {}
        still_has_chinese = {}
        
        for key, value in items.items():
            if self.has_chinese(value):
                still_has_chinese[key] = value
            else:
                successfully_translated[key] = value
        
        return successfully_translated, still_has_chinese
    
    def translate_single_item(self, text: str) -> str:
        """Translate a single item with focused prompt"""
        if not self.has_chinese(text):
            return text
        
        focused_prompt = f"""Translate ALL Chinese characters in this text to English. Keep everything else unchanged:

{text}

Return ONLY the translated text with ALL Chinese converted to English:"""
        
        try:
            result = self.gpt.query(focused_prompt)
            return result.strip()
        except Exception as e:
            print(f"单项翻译失败: {e}")
            return text
    
    def aggressive_translate_remaining(self, items: Dict[str, str]) -> Dict[str, str]:
        """Aggressively translate remaining Chinese items one by one"""
        print(f"开始逐项强化翻译 {len(items)} 个项目...")
        
        result = {}
        for i, (key, value) in enumerate(items.items(), 1):
            print(f"翻译项目 {i}/{len(items)}: {value[:50]}...")
            
            if self.has_chinese(value):
                # Try multiple times with different approaches
                translated = value
                
                # Attempt 1: Single item translation
                translated = self.translate_single_item(translated)
                
                # Attempt 2: If still has Chinese, split and translate parts
                if self.has_chinese(translated):
                    print(f"  仍含中文，尝试分段翻译...")
                    parts = re.split(r'([。！？；：\n]+)', translated)
                    translated_parts = []
                    
                    for part in parts:
                        if part.strip() and self.has_chinese(part):
                            translated_part = self.translate_single_item(part)
                            translated_parts.append(translated_part)
                        else:
                            translated_parts.append(part)
                    
                    translated = ''.join(translated_parts)
                
                result[key] = translated
            else:
                result[key] = value
            
            # Small delay to avoid rate limiting
            time.sleep(0.3)
        
        return result
    
    def translate_with_enhanced_retry(self, items: Dict[str, str]) -> Dict[str, str]:
        """
        Enhanced translation with multiple retry strategies
        """
        all_translated = {}
        remaining_items = items.copy()
        round_count = 0
        
        while remaining_items and round_count < self.max_retries:
            round_count += 1
            print(f"\n=== 第 {round_count} 轮翻译 ===")
            print(f"待翻译项目数量: {len(remaining_items)}")
            
            total_chinese = sum(self.count_chinese_chars(v) for v in remaining_items.values())
            print(f"待翻译中文字符总数: {total_chinese}")
            
            if round_count <= 5:
                # First 5 rounds: Use batch translation
                batches = self.create_small_batches(remaining_items)
                print(f"分为 {len(batches)} 个批次")
                
                # Translate each batch
                batch_results = {}
                for i, batch in enumerate(batches, 1):
                    print(f"\n处理批次 {i}/{len(batches)}")
                    translated_batch = self.translate_batch(batch, round_count)
                    batch_results.update(translated_batch)
                    
                    # Delay between batches
                    time.sleep(1)
                
                # Validate results
                successfully_translated, still_chinese = self.validate_translation(batch_results)
                
            else:
                # Later rounds: Use aggressive single-item translation
                print(f"使用强化单项翻译模式")
                batch_results = self.aggressive_translate_remaining(remaining_items)
                successfully_translated, still_chinese = self.validate_translation(batch_results)
            
            print(f"本轮成功翻译: {len(successfully_translated)} 项")
            print(f"本轮仍含中文: {len(still_chinese)} 项")
            
            # Add successfully translated items to final result
            all_translated.update(successfully_translated)
            
            # Prepare for next iteration
            if len(still_chinese) >= len(remaining_items):
                # No progress made, try different strategy
                print(f"翻译进度停滞，调整策略...")
                # Reduce batch size
                self.max_tokens_per_batch = max(500, self.max_tokens_per_batch // 2)
                print(f"减小批次大小到: {self.max_tokens_per_batch}")
            
            remaining_items = still_chinese
            
            if remaining_items:
                print(f"准备进入下一轮，剩余 {len(remaining_items)} 项...")
                time.sleep(2)  # Longer delay between rounds
        
        # Final check and reporting
        if remaining_items:
            print(f"\n警告: {len(remaining_items)} 项在 {self.max_retries} 轮翻译后仍包含中文字符")
            print("这些项目的前10个示例:")
            count = 0
            for key, value in remaining_items.items():
                if count >= 10:
                    break
                chinese_count = self.count_chinese_chars(value)
                display_value = value[:100] + "..." if len(value) > 100 else value
                print(f"  {count+1}. 中文字符数:{chinese_count} - '{display_value}'")
                count += 1
            
            # Add remaining items to result as-is
            all_translated.update(remaining_items)
        
        return all_translated
    
    def translate_json_file(self, input_file: str, output_file: str = None) -> bool:
        """
        Enhanced translation of JSON file from Chinese to English
        """
        print(f"增强版JSON翻译器 - 强力中文到英文翻译")
        print("=" * 60)
        
        # Validate input file
        if not os.path.exists(input_file):
            print(f"错误: 输入文件不存在: {input_file}")
            return False
        
        # Generate output file name if not provided
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_fully_translated.json"
        
        try:
            # Load JSON file
            print(f"正在加载JSON文件: {input_file}")
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"加载了 {len(data)} 个项目")
            
            # Analyze the content
            chinese_items = self.extract_chinese_items(data)
            english_items = {k: v for k, v in data.items() if k not in chinese_items}
            
            total_chinese_chars = sum(self.count_chinese_chars(v) for v in chinese_items.values())
            
            print(f"包含中文的项目: {len(chinese_items)}")
            print(f"已是英文的项目: {len(english_items)}")
            print(f"待翻译中文字符总数: {total_chinese_chars}")
            
            if not chinese_items:
                print("没有需要翻译的中文内容")
                return True
            
            # Enhanced translation
            print(f"\n开始强力翻译...")
            start_time = time.time()
            
            translated_items = self.translate_with_enhanced_retry(chinese_items)
            
            end_time = time.time()
            print(f"\n翻译完成，耗时: {end_time - start_time:.2f} 秒")
            
            # Combine results
            final_result = {}
            final_result.update(english_items)  # Add items that were already English
            final_result.update(translated_items)  # Add translated items
            
            # Save to output file
            print(f"正在保存到: {output_file}")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(final_result, f, ensure_ascii=False, indent=2)
            
            # Final statistics
            final_chinese_count = len([v for v in final_result.values() if self.has_chinese(v)])
            final_chinese_chars = sum(self.count_chinese_chars(v) for v in final_result.values())
            
            print(f"\n=== 最终翻译统计 ===")
            print(f"总项目数: {len(data)}")
            print(f"原本为英文: {len(english_items)}")
            print(f"成功完全翻译: {len(chinese_items) - final_chinese_count}")
            print(f"翻译后仍含中文的项目: {final_chinese_count}")
            print(f"翻译前中文字符数: {total_chinese_chars}")
            print(f"翻译后中文字符数: {final_chinese_chars}")
            print(f"翻译率: {((total_chinese_chars - final_chinese_chars) / total_chinese_chars * 100):.1f}%" if total_chinese_chars > 0 else "100%")
            print(f"输出文件: {output_file}")
            
            return True
            
        except Exception as e:
            print(f"处理过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main function to run the enhanced translator"""
    print("增强版JSON翻译器 - 强力中文到英文翻译")
    print("=" * 60)
    
    # Default to the specified file
    default_file = "translated_test_output_20250611植物提取物非临床安全性研究.json"
    
    if os.path.exists(default_file):
        print(f"发现目标文件: {default_file}")
        use_default = input(f"是否使用此文件进行翻译？(y/n): ").strip().lower()
        
        if use_default in ['y', 'yes', '是', '']:
            input_file = default_file
        else:
            input_file = input("请输入JSON文件路径: ").strip()
    else:
        input_file = input("请输入JSON文件路径: ").strip()
    
    if not input_file:
        print("未提供输入文件路径")
        return
    
    # Remove quotes if present
    if input_file.startswith('"') and input_file.endswith('"'):
        input_file = input_file[1:-1]
    
    # Create enhanced translator and process file
    translator = EnhancedJsonTranslator()
    success = translator.translate_json_file(input_file)
    
    if success:
        print("\n✓ 强力翻译完成！")
    else:
        print("\n✗ 翻译失败！")


if __name__ == "__main__":
    main() 