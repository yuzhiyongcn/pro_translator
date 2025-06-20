#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOCX文件内容提取器
读取docx文件的所有内容，按最小片段创建JSON文件
"""

import os
import json
import re
from docx import Document
from typing import Dict, List, Set


class DocxToJsonConverter:
    def __init__(self):
        """Initialize the converter"""
        self.fragments = set()  # Use set to avoid duplicates
    
    def extract_all_paragraphs(self, doc: Document) -> List:
        """
        Extract all paragraphs from document including:
        - Main body paragraphs
        - Table cell paragraphs
        - Header paragraphs
        - Footer paragraphs
        """
        paragraphs = []
        
        # Extract main document paragraphs
        paragraphs.extend(doc.paragraphs)
        
        # Extract table paragraphs
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    paragraphs.extend(cell.paragraphs)
        
        # Extract header and footer paragraphs
        for section in doc.sections:
            # Header paragraphs
            if section.header:
                paragraphs.extend(section.header.paragraphs)
                # Header tables
                for table in section.header.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            paragraphs.extend(cell.paragraphs)
            
            # Footer paragraphs
            if section.footer:
                paragraphs.extend(section.footer.paragraphs)
                # Footer tables
                for table in section.footer.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            paragraphs.extend(cell.paragraphs)
        
        return paragraphs
    
    def extract_text_fragments(self, text: str) -> List[str]:
        """
        Extract minimal text fragments from a text string
        Split by common delimiters while preserving meaningful units
        """
        if not text or not text.strip():
            return []
        
        # Remove extra whitespace
        text = text.strip()
        
        # Split by various delimiters but keep meaningful fragments
        # Split by sentences first (. ! ?)
        sentences = re.split(r'[.!?]+', text)
        
        fragments = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Further split by commas, semicolons, colons
            sub_fragments = re.split(r'[,;:]+', sentence)
            
            for fragment in sub_fragments:
                fragment = fragment.strip()
                if fragment:
                    # Split by whitespace for individual words/tokens
                    words = fragment.split()
                    for word in words:
                        word = word.strip()
                        if word and len(word) > 0:
                            fragments.append(word)
                    
                    # Also keep the phrase as a fragment if it's meaningful
                    if len(fragment) > 1:
                        fragments.append(fragment)
            
            # Keep the sentence as a fragment too
            if len(sentence) > 1:
                fragments.append(sentence)
        
        # Keep the original text as a fragment if it's meaningful
        if len(text) > 1:
            fragments.append(text)
        
        return fragments
    
    def process_docx_file(self, file_path: str) -> Dict[str, str]:
        """
        Process a DOCX file and extract all text fragments
        Returns a dictionary with fragment as both key and value
        """
        print(f"正在处理文件: {file_path}")
        
        try:
            doc = Document(file_path)
        except Exception as e:
            print(f"无法打开DOCX文件: {e}")
            return {}
        
        # Extract all paragraphs
        paragraphs = self.extract_all_paragraphs(doc)
        
        print(f"找到 {len(paragraphs)} 个段落")
        
        # Process each paragraph
        for paragraph in paragraphs:
            text = paragraph.text
            if text and text.strip():
                # Extract fragments from paragraph text
                fragments = self.extract_text_fragments(text)
                
                # Add fragments to our set (avoids duplicates)
                for fragment in fragments:
                    if fragment and len(fragment.strip()) > 0:
                        self.fragments.add(fragment.strip())
        
        # Convert set to dictionary with fragment as both key and value
        result_dict = {}
        for fragment in self.fragments:
            result_dict[fragment] = fragment
        
        return result_dict
    
    def save_to_json(self, data: Dict[str, str], output_path: str):
        """Save the fragments dictionary to a JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"JSON文件已保存到: {output_path}")
        except Exception as e:
            print(f"保存JSON文件失败: {e}")
    
    def convert_file(self, input_file: str, output_file: str = None):
        """
        Convert a DOCX file to JSON format
        
        Args:
            input_file: Path to input DOCX file
            output_file: Path to output JSON file (optional)
        """
        if not os.path.exists(input_file):
            print(f"输入文件不存在: {input_file}")
            return
        
        if not input_file.lower().endswith('.docx'):
            print(f"输入文件必须是DOCX格式: {input_file}")
            return
        
        # Generate output file name if not provided
        if output_file is None:
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = f"{base_name}_fragments.json"
        
        # Process the DOCX file
        fragments_dict = self.process_docx_file(input_file)
        
        if not fragments_dict:
            print("未找到任何文本内容")
            return
        
        # Save to JSON
        self.save_to_json(fragments_dict, output_file)
        
        # Print statistics
        print(f"\n=== 统计信息 ===")
        print(f"JSON文件item数量: {len(fragments_dict)}")
        print(f"处理的唯一文本片段数量: {len(self.fragments)}")
        
        return fragments_dict


def main():
    """Main function to run the converter"""
    print("DOCX文件内容提取器")
    print("=" * 50)
    
    # Get input file from user
    input_file = input("请输入DOCX文件路径: ").strip()
    
    if not input_file:
        print("未提供输入文件路径")
        return
    
    # Remove quotes if present
    if input_file.startswith('"') and input_file.endswith('"'):
        input_file = input_file[1:-1]
    
    # Create converter and process file
    converter = DocxToJsonConverter()
    converter.convert_file(input_file)


if __name__ == "__main__":
    main() 