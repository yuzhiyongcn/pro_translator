from openai import OpenAI
import os
from docx import Document
from gpt_translator import GPTTranslator
from concurrent.futures import ThreadPoolExecutor
import json


# 设置 OpenAI API 密钥
class DocTranslator:
    def __init__(self, num_threads=12):
        self.num_threads = num_threads
        terminology = {}
        file = "config.json"
        with open(file, "r", encoding="utf-8") as f:
            terminology = json.load(f)

        self.translator = GPTTranslator(terminology)

    def __translate_text(self, text):
        # return self.translator.translate(text)
        return text

    def __translate_element(self, element, new_doc):
        """
        复制段落或表格到新文档中，并保持格式
        """
        if element.tag.endswith("p"):
            new_paragraph = new_doc.add_paragraph()
            new_paragraph.alignment = element.alignment
            if hasattr(element, "paragraph_format"):
                new_paragraph.paragraph_format.left_indent = (
                    element.paragraph_format.left_indent
                )
                new_paragraph.paragraph_format.right_indent = (
                    element.paragraph_format.right_indent
                )
                new_paragraph.paragraph_format.space_before = (
                    element.paragraph_format.space_before
                )
                new_paragraph.paragraph_format.space_after = (
                    element.paragraph_format.space_after
                )
                new_paragraph.paragraph_format.line_spacing = (
                    element.paragraph_format.line_spacing
                )

            if hasattr(element, "runs"):
                for run in element.runs:
                    new_run = new_paragraph.add_run(run.text)
                    new_run.bold = run.bold
                    new_run.italic = run.italic
                    new_run.underline = run.underline
                    if run.font.name:
                        new_run.font.name = run.font.name
                    if run.font.size:
                        new_run.font.size = run.font.size
                    if run.font.color.rgb:
                        new_run.font.color.rgb = run.font.color.rgb
                    new_run.font.highlight_color = run.font.highlight_color

        elif element.tag.endswith("tbl"):
            if hasattr(element, "runs"):
                new_table = new_doc.add_table(rows=0, cols=0)
                for row in element.rows:
                    new_row = new_table.add_row()
                    for cell_index, cell in enumerate(row.cells):
                        new_cell = new_row.cells[cell_index]
                        new_cell.text = cell.text
                        new_cell_paragraph = new_cell.paragraphs[0]
                        new_cell_paragraph.alignment = cell.paragraphs[0].alignment
                        new_cell_paragraph.paragraph_format.left_indent = (
                            cell.paragraphs[0].paragraph_format.left_indent
                        )
                        new_cell_paragraph.paragraph_format.right_indent = (
                            cell.paragraphs[0].paragraph_format.right_indent
                        )
                        new_cell_paragraph.paragraph_format.space_before = (
                            cell.paragraphs[0].paragraph_format.space_before
                        )
                        new_cell_paragraph.paragraph_format.space_after = (
                            cell.paragraphs[0].paragraph_format.space_after
                        )
                        new_cell_paragraph.paragraph_format.line_spacing = (
                            cell.paragraphs[0].paragraph_format.line_spacing
                        )

        elif element.tag.endswith("drawing") or element.tag.endswith("pic"):
            self.__copy_picture(element, new_doc)

    def __copy_picture(self, element, new_doc):
        """
        复制图片到新文档中
        """
        # 找到所有的图片数据
        rels = element.part.rels
        for rel in rels:
            if "image" in rels[rel].target_ref:
                image_path = rels[rel].target_part.blob
                with open(image_path, "rb") as img_file:
                    image_data = img_file.read()
                temp_img_path = "temp_img.png"
                with open(temp_img_path, "wb") as temp_img:
                    temp_img.write(image_data)
                new_doc.add_picture(temp_img_path)
                os.remove(temp_img_path)

    def __translate_elements(self, elements, result_list, index):
        """
        复制文档元素到一个临时文档，并保存到结果列表中
        """
        temp_doc = Document()
        count = 0
        for element in elements:
            self.__translate_element(element, temp_doc)
            print(f"线程 {index} 处理完第 {index + count} 个段落")
            count += 1
        result_list[index] = temp_doc

    def translate(self, file):
        # 复制文件

        # 打开原始文档
        source_doc = Document(file)

        # 获取原文档中的所有元素
        elements = list(source_doc.element.body.iterchildren())

        # 分成num_threads个部分
        chunk_size = len(elements) // self.num_threads
        print(f"共有{len(elements)}个段落，每个线程处理{chunk_size}个段落")
        chunks = []
        for i in range(self.num_threads):
            start = i * chunk_size
            if i == self.num_threads - 1:  # 最后一个线程处理剩余的所有元素
                end = len(elements)
            else:
                end = (i + 1) * chunk_size
            chunks.append(list(elements)[start:end])

        # 创建一个结果列表来保存中间文档
        results = [None] * self.num_threads

        # 创建线程池
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = [
                executor.submit(self.__translate_elements, chunk, results, i)
                for i, chunk in enumerate(chunks)
            ]
            for future in futures:
                future.result()  # 等待所有线程完成

        # 创建最终文档并合并所有中间文档
        new_doc = Document()
        for temp_doc in results:
            for element in temp_doc.element.body.iterchildren():
                self.__translate_element(element, new_doc)

        # 保存新的文档
        dest_file = file.replace(".docx", "-translated.docx")
        new_doc.save(dest_file)


if __name__ == "__main__":
    translator = DocTranslator()
    translator.translate("111-EN.docx")
