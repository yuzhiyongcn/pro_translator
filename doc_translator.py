from openai import OpenAI
import os
from docx import Document
import re
from gpt_translator import GPTTranslator


# 设置 OpenAI API 密钥
class DocTranslator:
    def __init__(self):
        terminology = {}
        self.translator = GPTTranslator(terminology)

    def translate(self, file):
        file_name = os.path.basename(file)
        new_file_name = file_name.replace(".docx", "_translated.docx")
        document = Document(file)
        new_document = Document()
        for para in document.paragraphs:
            new_paragraph = new_document.add_paragraph()
            for run in para.runs:
                translated_text = self.translator.translate(run.text)
                new_run = new_paragraph.add_run(translated_text)
                new_run.font.name = run.font.name
                new_run.font.size = run.font.size
                new_run.font.bold = run.font.bold
                new_run.font.italic = run.font.italic
                new_run.font.underline = run.font.underline
                if run.font.color:
                    new_run.font.color.rgb = run.font.color.rgb

        for table in document.tables:
            new_table = new_document.add_table(
                rows=len(table.rows), cols=len(table.columns)
            )
            for i, row in enumerate(table.rows):
                for j, cell in enumerate(row.cells):
                    translated_text = self.translator.translate(cell.text)
                    new_table.cell(i, j).text = translated_text

        new_document.save(file.replace(file_name, new_file_name))
