#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试步骤3：替换DOCX内容
使用已经准备好的翻译JSON文件来替换原始DOCX文件的内容
"""

import os
import sys
from docx_translator_complete import CompleteDocxTranslator


def test_step3_replace_docx():
    """Test Step 3: Replace DOCX content with translated JSON"""
    
    print("测试步骤3：替换DOCX内容")
    print("=" * 60)
    
    # File paths
    original_docx = "../input/source/20250611植物提取物非临床安全性研究.docx"
    translated_json = "fully_translated_test_output_20250611植物提取物非临床安全性研究.json"
    output_docx = "20250611植物提取物非临床安全性研究_step3_translated.docx"
    
    print(f"原始DOCX文件: {original_docx}")
    print(f"翻译JSON文件: {translated_json}")
    print(f"输出DOCX文件: {output_docx}")
    print()
    
    # Check if files exist
    if not os.path.exists(original_docx):
        print(f"❌ 原始DOCX文件不存在: {original_docx}")
        return False
    
    if not os.path.exists(translated_json):
        print(f"❌ 翻译JSON文件不存在: {translated_json}")
        return False
    
    print("✓ 所有必需文件都存在")
    print()
    
    try:
        # Create translator instance
        translator = CompleteDocxTranslator()
        
        # Execute Step 3 only
        print("开始执行步骤3...")
        result_docx = translator.step3_replace_docx_content(
            original_docx=original_docx,
            translated_json=translated_json,
            output_docx=output_docx
        )
        
        print(f"\n🎉 步骤3测试成功完成！")
        print(f"📁 翻译后的DOCX文件: {result_docx}")
        
        # Verify output file exists
        if os.path.exists(result_docx):
            file_size = os.path.getsize(result_docx)
            print(f"📄 输出文件大小: {file_size:,} 字节")
            print("\n建议手动打开文件检查翻译效果")
        else:
            print("❌ 输出文件不存在")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 步骤3测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    success = test_step3_replace_docx()
    
    if success:
        print("\n✅ 步骤3测试成功")
    else:
        print("\n❌ 步骤3测试失败")
    
    return success


if __name__ == "__main__":
    main() 