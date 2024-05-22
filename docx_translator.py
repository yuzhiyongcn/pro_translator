import os
from docx import Document
from gpt_translator import GPTTranslator
import json
import shutil
import time


class DocTranslator:
    def __init__(self):
        terminology = self._load_terminology("terminology.txt")
        print(f"术语表: {json.dumps(terminology, indent=4)}")

        self.translator = GPTTranslator(terminology)
        self.excludes = ["F", "Y", "N", "-", "+"]
        self.debug_mode = True

    def _load_terminology(self, file_path):
        data = {}
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                # 去除每行的空白符
                line = line.strip()
                if line:
                    # 分割成键值对
                    key, value = line.split("=", 1)
                    # 去除键和值两端的空白符
                    key = key.strip()
                    value = value.strip()
                    # 添加到字典中
                    data[key] = value
        return data

    def _translate_text(self, text):
        if text in self.excludes:
            return text
        if text.replace(" ", "").isdigit():
            return text
        if text.replace(" ", "").replace("Ä", "") == "":
            return text.replace("Ä", "-")

        return self.translator.translate(text)

    def _copy_file(self, source_file, dest_file):
        try:
            shutil.copyfile(source_file, dest_file)
        except Exception as e:
            print(f"文件复制失败: {e}")

    def _translate_paragraph(self, index, paragraph):
        print(f"############# 正在处理 {self.part} 第 {index} 个段落 #############")
        if paragraph.text.strip():
            translated_text = self._translate_text(paragraph.text)
            translated_text = paragraph.text.replace(
                paragraph.text.strip(), translated_text.strip()
            )

            # 输出原文和译文
            orgin_msg = f"原文: {paragraph.text}"
            translated_msg = f"译文: {translated_text}"
            print(orgin_msg)
            print(translated_msg)
            if self.debug_mode:
                self.debug_file.write(orgin_msg + "\n")
                self.debug_file.write(translated_msg + "\n")
                self.debug_file.write(
                    "--------------------------------------------------\n"
                )

            paragraph.text = translated_text

    def _translate_paragraphs(self, paragraphs):
        paragraphs = [paragraph for paragraph in paragraphs if paragraph.text.strip()]
        # 只处理前30个
        paragraphs = paragraphs[:60]

        for index, item in enumerate(paragraphs):
            self._translate_paragraph(index, item)

    def _translate_tables(self, tables):
        paragraphs = []
        for table in tables:
            for row in table.rows:
                for cell in row.cells:
                    paragraphs.extend(cell.paragraphs)
        self._translate_paragraphs(paragraphs)

    def _translate_headers(self, headers):
        paragraphs = []
        for header in headers:
            paragraphs.extend(header.paragraphs)
            for table in header.tables:
                for row in table.rows:
                    for cell in row.cells:
                        paragraphs.extend(cell.paragraphs)
        self._translate_paragraphs(paragraphs)

    def _translate_footers(self, footers):
        paragraphs = []
        for footer in footers:
            paragraphs.extend(footer.paragraphs)
            for table in footer.tables:
                for row in table.rows:
                    for cell in row.cells:
                        paragraphs.extend(cell.paragraphs)
        self._translate_paragraphs(paragraphs)

    def translate(self, file):
        start = time.time()
        self.debug_file_path = file.replace(".docx", "-debug.txt")

        # 复制文件
        translated_file = file.replace(".docx", "-translated.docx")
        self._copy_file(file, translated_file)

        doc = Document(translated_file)

        with open(self.debug_file_path, "w", encoding="utf-8") as debug_file:
            self.debug_file = debug_file
            # 翻译页眉
            self.part = "页眉"
            headers = [section.header for section in doc.sections]
            self._translate_headers([headers[0]])

            # 翻译页脚
            self.part = "页脚"
            footers = [section.footer for section in doc.sections]
            self._translate_footers([footers[0]])

            # 翻译shapes
            self.part = "shapes"
            shapes = []
            for shape in doc.inline_shapes:
                shapes.append(shape)
            self._translate_paragraphs(shapes)

            # 翻译段落
            self.part = "段落"
            self._translate_paragraphs(doc.paragraphs)

            # 翻译表格
            self.part = "表格"
            self._translate_tables(doc.tables)

        # 保存文件
        doc.save(translated_file)

        end = time.time()
        print(f"翻译完成，用时: {end - start:.2f} 秒")


if __name__ == "__main__":
    translator = DocTranslator()
    translator.translate("NSR_T103508-7_PH-42754_DRF dog.docx")
