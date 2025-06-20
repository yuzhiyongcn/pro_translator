#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的DOCX翻译程序
包含三个步骤：1. DOCX转JSON  2. JSON翻译  3. 替换DOCX内容
"""

import os
import sys
import json
import shutil
from typing import Dict, List, Tuple

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from docx import Document
from docx.shared import RGBColor
from docx_to_json import DocxToJsonConverter
from json_translator_enhanced import EnhancedJsonTranslator


class CompleteDocxTranslator:
    def __init__(self):
        """Initialize the complete DOCX translator"""
        self.docx_converter = DocxToJsonConverter()
        self.json_translator = EnhancedJsonTranslator()
    
    def step1_docx_to_json(self, docx_file: str, json_file: str = None) -> str:
        """
        Step 1: Convert DOCX file to JSON fragments
        
        Args:
            docx_file: Path to input DOCX file
            json_file: Path to output JSON file (optional)
            
        Returns:
            Path to generated JSON file
        """
        print("=== 步骤1: DOCX转JSON ===")
        
        if not os.path.exists(docx_file):
            raise FileNotFoundError(f"DOCX文件不存在: {docx_file}")
        
        if json_file is None:
            base_name = os.path.splitext(docx_file)[0]
            json_file = f"{base_name}_fragments.json"
        
        print(f"输入文件: {docx_file}")
        print(f"输出文件: {json_file}")
        
        # Convert DOCX to JSON
        result = self.docx_converter.convert_file(docx_file, json_file)
        
        if result:
            print(f"✓ 成功转换为JSON，共 {len(result)} 个文本片段")
            return json_file
        else:
            raise Exception("DOCX转JSON失败")
    
    def step2_translate_json(self, input_json: str, output_json: str = None) -> str:
        """
        Step 2: Translate JSON file from Chinese to English
        
        Args:
            input_json: Path to input JSON file
            output_json: Path to output translated JSON file (optional)
            
        Returns:
            Path to translated JSON file
        """
        print("=== 步骤2: JSON翻译 ===")
        
        if not os.path.exists(input_json):
            raise FileNotFoundError(f"JSON文件不存在: {input_json}")
        
        if output_json is None:
            base_name = os.path.splitext(input_json)[0]
            output_json = f"{base_name}_translated.json"
        
        print(f"输入文件: {input_json}")
        print(f"输出文件: {output_json}")
        
        # Translate JSON
        success = self.json_translator.translate_json_file(input_json, output_json)
        
        if success:
            print(f"✓ JSON翻译完成")
            return output_json
        else:
            raise Exception("JSON翻译失败")
    
    def step3_replace_docx_content(self, original_docx: str, translated_json: str, output_docx: str = None) -> str:
        """
        Step 3: Replace DOCX content with translated text
        
        Args:
            original_docx: Path to original DOCX file
            translated_json: Path to translated JSON file
            output_docx: Path to output DOCX file (optional)
            
        Returns:
            Path to output DOCX file
        """
        print("=== 步骤3: 替换DOCX内容 ===")
        
        if not os.path.exists(original_docx):
            raise FileNotFoundError(f"原始DOCX文件不存在: {original_docx}")
        
        if not os.path.exists(translated_json):
            raise FileNotFoundError(f"翻译JSON文件不存在: {translated_json}")
        
        if output_docx is None:
            base_name = os.path.splitext(original_docx)[0]
            output_docx = f"{base_name}_translated.docx"
        
        print(f"原始DOCX: {original_docx}")
        print(f"翻译JSON: {translated_json}")
        print(f"输出DOCX: {output_docx}")
        
        # Load translated JSON
        with open(translated_json, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        
        print(f"加载了 {len(translations)} 个翻译项目")
        
        # Copy original DOCX file
        shutil.copy2(original_docx, output_docx)
        print(f"已复制原始DOCX文件")
        
        # Load the copied DOCX file
        doc = Document(output_docx)
        
        replacement_stats = {
            'total_replacements': 0,
            'paragraph_replacements': 0,
            'table_replacements': 0,
            'header_footer_replacements': 0
        }
        
        # Replace text in main document paragraphs
        replacement_stats['paragraph_replacements'] += self._replace_in_paragraphs(
            doc.paragraphs, translations, "主文档段落"
        )
        
        # Replace text in tables
        for table_idx, table in enumerate(doc.tables):
            for row_idx, row in enumerate(table.rows):
                for cell_idx, cell in enumerate(row.cells):
                    replacements = self._replace_in_paragraphs(
                        cell.paragraphs, translations, f"表格{table_idx+1}-行{row_idx+1}-列{cell_idx+1}"
                    )
                    replacement_stats['table_replacements'] += replacements
        
        # Replace text in headers and footers
        for section in doc.sections:
            # Headers
            if section.header:
                replacements = self._replace_in_paragraphs(
                    section.header.paragraphs, translations, "页眉"
                )
                replacement_stats['header_footer_replacements'] += replacements
            
            # Footers
            if section.footer:
                replacements = self._replace_in_paragraphs(
                    section.footer.paragraphs, translations, "页脚"
                )
                replacement_stats['header_footer_replacements'] += replacements
        
        # Save the modified document
        doc.save(output_docx)
        
        # Calculate total replacements
        replacement_stats['total_replacements'] = (
            replacement_stats['paragraph_replacements'] +
            replacement_stats['table_replacements'] +
            replacement_stats['header_footer_replacements']
        )
        
        print(f"\n=== 替换统计 ===")
        print(f"主文档段落替换: {replacement_stats['paragraph_replacements']}")
        print(f"表格内容替换: {replacement_stats['table_replacements']}")
        print(f"页眉页脚替换: {replacement_stats['header_footer_replacements']}")
        print(f"总替换次数: {replacement_stats['total_replacements']}")
        print(f"✓ DOCX内容替换完成")
        
        return output_docx
    
    def _replace_in_paragraphs(self, paragraphs, translations: Dict[str, str], location: str) -> int:
        """
        Replace text in paragraphs using translation dictionary
        
        Args:
            paragraphs: List of paragraph objects
            translations: Dictionary of original -> translated text
            location: Location description for logging
            
        Returns:
            Number of replacements made
        """
        replacement_count = 0
        
        for para_idx, paragraph in enumerate(paragraphs):
            if not paragraph.text.strip():
                continue
            
            original_text = paragraph.text
            modified = False
            
            # Try to replace with translation mappings
            # Sort by length (longest first) to avoid partial replacements
            sorted_translations = sorted(translations.items(), key=lambda x: len(x[0]), reverse=True)
            
            for original, translated in sorted_translations:
                if original in original_text:
                    # Replace in the paragraph text
                    new_text = original_text.replace(original, translated)
                    if new_text != original_text:
                        # Clear existing runs and add new text
                        paragraph.clear()
                        run = paragraph.add_run(new_text)
                        
                        original_text = new_text
                        modified = True
                        replacement_count += 1
                        
                        print(f"  替换 {location}[{para_idx+1}]: {original[:30]}... -> {translated[:30]}...")
            
            if modified and replacement_count % 50 == 0:
                print(f"  已完成 {replacement_count} 次替换...")
        
        return replacement_count
    
    def translate_complete_workflow(self, docx_file: str, output_docx: str = None) -> str:
        """
        Complete workflow: DOCX -> JSON -> Translate -> Replace DOCX
        
        Args:
            docx_file: Path to input DOCX file
            output_docx: Path to output translated DOCX file (optional)
            
        Returns:
            Path to translated DOCX file
        """
        print("=== 完整DOCX翻译工作流程 ===")
        print(f"输入文件: {docx_file}")
        
        if output_docx is None:
            base_name = os.path.splitext(docx_file)[0]
            output_docx = f"{base_name}_fully_translated.docx"
        
        try:
            # Step 1: DOCX to JSON
            json_file = self.step1_docx_to_json(docx_file)
            
            # Step 2: Translate JSON
            translated_json = self.step2_translate_json(json_file)
            
            # Step 3: Replace DOCX content
            result_docx = self.step3_replace_docx_content(docx_file, translated_json, output_docx)
            
            print(f"\n🎉 完整翻译工作流程完成！")
            print(f"📁 输出文件: {result_docx}")
            
            return result_docx
            
        except Exception as e:
            print(f"❌ 翻译工作流程失败: {e}")
            raise


def main():
    """Main function for testing"""
    print("完整DOCX翻译程序")
    print("=" * 50)
    
    # Default input file
    default_docx = "../input/source/20250611植物提取物非临床安全性研究.docx"
    
    if os.path.exists(default_docx):
        print(f"发现默认文件: {default_docx}")
        translator = CompleteDocxTranslator()
        translator.translate_complete_workflow(default_docx)
    else:
        print(f"默认文件不存在: {default_docx}")
        print("请手动指定DOCX文件路径")


if __name__ == "__main__":
    main() 