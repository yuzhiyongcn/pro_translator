#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON翻译器
使用GPT-4o-mini批量翻译JSON文件中的中文内容到英文
"""

import os
import sys
import json
import re
import time
from typing import Dict, List, Tuple

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gpt_wrapper import GPTWrapper
import string_utils as su


class JsonTranslator:
    def __init__(self, model="gpt-4o-mini"):
        """Initialize the JSON translator"""
        self.model = model
        self.gpt = GPTWrapper(model=model)
        self.max_tokens_per_batch = 2000  # Conservative limit for batch processing
        self.separator = "[#]"
        
        # Set up system prompt for translation
        system_prompt = """You are a professional translator specializing in Chinese to English translation.

Rules:
1. Translate ONLY Chinese characters to English
2. Keep English letters, numbers, symbols, and abbreviations unchanged
3. Preserve spacing and formatting exactly as provided
4. Do not add explanations or extra text
5. Return only the translated text

Input format: Multiple text fragments separated by '[#]'
Output format: Translated fragments separated by '[#]' in the same order

Example:
Input: "测试文本[#]Hello World[#]数字123保持不变[#]English text"
Output: "test text[#]Hello World[#]number 123 remains unchanged[#]English text"
"""
        self.gpt.set_system_prompt(system_prompt)
    
    def has_chinese(self, text: str) -> bool:
        """Check if text contains Chinese characters"""
        return su.has_chinese(text)
    
    def extract_chinese_items(self, items: Dict[str, str]) -> Dict[str, str]:
        """Extract items that contain Chinese characters"""
        chinese_items = {}
        for key, value in items.items():
            if self.has_chinese(value):
                chinese_items[key] = value
        return chinese_items
    
    def estimate_token_count(self, text: str) -> int:
        """Estimate token count for a text string"""
        # Rough estimation: 1 token ≈ 4 characters for mixed Chinese/English text
        return len(text) // 3
    
    def create_batches(self, items: Dict[str, str]) -> List[Dict[str, str]]:
        """Create batches of items that fit within token limits"""
        batches = []
        current_batch = {}
        current_token_count = 0
        
        for key, value in items.items():
            estimated_tokens = self.estimate_token_count(value)
            
            # If adding this item would exceed the limit, start a new batch
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
    
    def translate_batch(self, batch: Dict[str, str]) -> Dict[str, str]:
        """Translate a batch of items"""
        if not batch:
            return {}
        
        # Create input text with separator
        keys = list(batch.keys())
        values = list(batch.values())
        input_text = self.separator.join(values)
        
        try:
            print(f"正在翻译批次，包含 {len(batch)} 个项目...")
            print(f"输入文本长度: {len(input_text)} 字符")
            
            # Call GPT for translation
            translated_text = self.gpt.query(input_text)
            
            # Split the translated text
            translated_values = translated_text.split(self.separator)
            
            # Verify the count matches
            if len(translated_values) != len(values):
                print(f"警告: 翻译前后数量不匹配！")
                print(f"原始数量: {len(values)}, 翻译后数量: {len(translated_values)}")
                print(f"原始文本: {input_text[:200]}...")
                print(f"翻译文本: {translated_text[:200]}...")
                
                # If counts don't match, return original items
                return batch
            
            # Create result dictionary
            result = {}
            for i, key in enumerate(keys):
                result[key] = translated_values[i].strip()
            
            return result
            
        except Exception as e:
            print(f"翻译批次时发生错误: {e}")
            return batch
    
    def validate_translation(self, items: Dict[str, str]) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Validate translation results
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
    
    def translate_with_retry(self, items: Dict[str, str], max_retries: int = 3) -> Dict[str, str]:
        """
        Translate items with retry logic for items that still contain Chinese
        """
        all_translated = {}
        remaining_items = items.copy()
        retry_count = 0
        
        while remaining_items and retry_count < max_retries:
            print(f"\n=== 第 {retry_count + 1} 轮翻译 ===")
            print(f"待翻译项目数量: {len(remaining_items)}")
            
            # Create batches for remaining items
            batches = self.create_batches(remaining_items)
            print(f"分为 {len(batches)} 个批次")
            
            # Translate each batch
            batch_results = {}
            for i, batch in enumerate(batches, 1):
                print(f"\n处理批次 {i}/{len(batches)}")
                translated_batch = self.translate_batch(batch)
                batch_results.update(translated_batch)
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
            
            # Validate results
            successfully_translated, still_chinese = self.validate_translation(batch_results)
            
            print(f"成功翻译: {len(successfully_translated)} 项")
            print(f"仍含中文: {len(still_chinese)} 项")
            
            # Add successfully translated items to final result
            all_translated.update(successfully_translated)
            
            # Prepare for next iteration
            remaining_items = still_chinese
            retry_count += 1
            
            if remaining_items:
                print(f"准备重试剩余 {len(remaining_items)} 项...")
        
        # If there are still items with Chinese after max retries
        if remaining_items:
            print(f"\n警告: {len(remaining_items)} 项在 {max_retries} 次重试后仍包含中文字符")
            print("这些项目将保持原样:")
            for key, value in list(remaining_items.items())[:5]:  # Show first 5
                print(f"  '{key}': '{value[:50]}...' " if len(value) > 50 else f"  '{key}': '{value}'")
            
            # Add remaining items to result as-is
            all_translated.update(remaining_items)
        
        return all_translated
    
    def translate_json_file(self, input_file: str, output_file: str = None) -> bool:
        """
        Translate a JSON file from Chinese to English
        
        Args:
            input_file: Path to input JSON file
            output_file: Path to output JSON file (optional)
        
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"JSON翻译器 - 中文到英文")
        print("=" * 50)
        
        # Validate input file
        if not os.path.exists(input_file):
            print(f"错误: 输入文件不存在: {input_file}")
            return False
        
        # Generate output file name if not provided
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_translated.json"
        
        try:
            # Load JSON file
            print(f"正在加载JSON文件: {input_file}")
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"加载了 {len(data)} 个项目")
            
            # Extract items that contain Chinese
            chinese_items = self.extract_chinese_items(data)
            english_items = {k: v for k, v in data.items() if k not in chinese_items}
            
            print(f"包含中文的项目: {len(chinese_items)}")
            print(f"已是英文的项目: {len(english_items)}")
            
            if not chinese_items:
                print("没有需要翻译的中文内容")
                return True
            
            # Translate Chinese items
            print(f"\n开始翻译...")
            start_time = time.time()
            
            translated_items = self.translate_with_retry(chinese_items)
            
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
            print(f"\n=== 翻译统计 ===")
            print(f"总项目数: {len(data)}")
            print(f"原本为英文: {len(english_items)}")
            print(f"成功翻译: {len([v for v in translated_items.values() if not self.has_chinese(v)])}")
            print(f"翻译后仍含中文: {len([v for v in translated_items.values() if self.has_chinese(v)])}")
            print(f"输出文件: {output_file}")
            
            return True
            
        except Exception as e:
            print(f"处理过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main function to run the translator"""
    print("JSON翻译器 - 中文到英文")
    print("=" * 50)
    
    # Get input file from user
    input_file = input("请输入JSON文件路径: ").strip()
    
    if not input_file:
        print("未提供输入文件路径")
        return
    
    # Remove quotes if present
    if input_file.startswith('"') and input_file.endswith('"'):
        input_file = input_file[1:-1]
    
    # Create translator and process file
    translator = JsonTranslator()
    success = translator.translate_json_file(input_file)
    
    if success:
        print("\n✓ 翻译完成！")
    else:
        print("\n✗ 翻译失败！")


if __name__ == "__main__":
    main() 