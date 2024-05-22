import os
from docx import Document
from gpt_translator import GPTTranslator
import json
import shutil
import time


class DocTranslator:
    def __init__(self, num_threads=16):
        self.num_threads = num_threads
        terminology = self.__load_terminology("terminology.txt")
        print(f"术语表: {json.dumps(terminology, indent=4)}")

        self.translator = GPTTranslator(terminology)
        self.excludes = ["F", "Y", "N", "-", "+"]
        self.debug_mode = True

    def __load_terminology(self, file_path):
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

    def __translate_text(self, text):
        return self.translator.translate(text)

    def __copy_file(self, source_file, dest_file):
        try:
            shutil.copyfile(source_file, dest_file)
        except Exception as e:
            print(f"文件复制失败: {e}")

    def __split_list(self, alist, chunk_size=10):
        # 使用列表切片，将alist按每chunk_size个元素分割成多个数组
        return [alist[i : i + chunk_size] for i in range(0, len(alist), chunk_size)]

    def __translate_paragraph_groups(self, paragraph_groups):
        for index, group in enumerate(paragraph_groups):
            print(f"############# 正在处理第 {index} 组段落 #############")
            group_text = [p.text for p in group]
            translated_group_text = self.__translate_text(group_text)
            for i, paragraph in enumerate(group):
                print(
                    f"############# 正在处理第 {index} 组, 第 {i} 个段落 #############"
                )
                translated_text = translated_group_text[i]
                # translated_text = paragraph.text.replace(
                #     paragraph.text.strip(), translated_text
                # )
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

    def __translate_paragraphs(self, paragraphs):
        paragraphs = [
            p
            for p in paragraphs
            if p.text.strip() and p.text.strip() not in self.excludes
        ]
        # 只处理前30个
        # paragraphs = paragraphs[:30]

        paragraph_groups = self.__split_list(paragraphs, 10)
        self.__translate_paragraph_groups(paragraph_groups)

    def __translate_tables(self, tables):
        paragraphs = []
        for table in tables:
            for row in table.rows:
                for cell in row.cells:
                    paragraphs.extend(cell.paragraphs)
        self.__translate_paragraphs(paragraphs)

    def __translate_headers(self, headers):
        paragraphs = []
        for header in headers:
            paragraphs.extend(header.paragraphs)
            for table in header.tables:
                for row in table.rows:
                    for cell in row.cells:
                        paragraphs.extend(cell.paragraphs)
        self.__translate_paragraphs(paragraphs)

    def __translate_footers(self, footers):
        paragraphs = []
        for footer in footers:
            paragraphs.extend(footer.paragraphs)
            for table in footer.tables:
                for row in table.rows:
                    for cell in row.cells:
                        paragraphs.extend(cell.paragraphs)
        self.__translate_paragraphs(paragraphs)

    def translate(self, file):
        start = time.time()
        self.debug_file_path = file.replace(".docx", "-debug.txt")

        # 复制文件
        translated_file = file.replace(".docx", "-translated.docx")
        self.__copy_file(file, translated_file)

        doc = Document(translated_file)

        with open(self.debug_file_path, "w", encoding="utf-8") as debug_file:
            self.debug_file = debug_file
            # 翻译页眉
            headers = [section.header for section in doc.sections]
            self.__translate_headers([headers[0]])

            # 翻译页脚
            footers = [section.footer for section in doc.sections]
            self.__translate_footers([footers[0]])

            # 翻译shapes
            shapes = []
            for shape in doc.inline_shapes:
                shapes.append(shape)
            self.__translate_paragraphs(shapes)

            # 翻译段落
            self.__translate_paragraphs(doc.paragraphs)

            # 翻译表格
            self.__translate_tables(doc.tables)

        # 保存文件
        doc.save(translated_file)

        end = time.time()
        print(f"翻译完成，用时: {end - start:.2f} 秒")


if __name__ == "__main__":
    translator = DocTranslator()
    translator.translate("NSR_T103508-7_PH-42754_DRF dog.docx")
