import os
from docx import Document
from gpt_translator import GPTTranslator
import json
import shutil
import time
import terms_persister as persister
import string_utils as su
import file_utils as fu


class DocTranslator:
    def __init__(self, to_CN=True):
        self.to_CN = to_CN
        terms_file = r"input\terms_en2zh.xlsx" if to_CN else r"input\terms_zh2en.xlsx"
        self.terms = persister.read_from_excel(terms_file)

        additional_terms = (
            r"input\additional_terms_en2zh.json"
            if to_CN
            else r"input\additional_terms_zh2en.json"
        )
        self.terms.update(fu.read_json_file(additional_terms))

        print(f"术语表单词数量: {len(self.terms)}")

        self.translator = GPTTranslator(to_CN)
        self.excludes = ["F", "Y", "N", "-", "+"]
        self.debug_mode = True

    def _translate_text(self, text):
        if text in self.excludes:
            return text
        if text.replace(" ", "").isdigit():
            return text

        return self.translator.translate(text)

    def _copy_file(self, source_file, dest_file):
        try:
            shutil.copyfile(source_file, dest_file)
        except Exception as e:
            print(f"文件复制失败: {e}")

    def __load_tables(self, tables):
        paragraphs = []
        for table in tables:
            for row in table.rows:
                for cell in row.cells:
                    paragraphs.extend(cell.paragraphs)
        return paragraphs

    def __load_headers_or_footers(self, headers_or_footers):
        paragraphs = []
        for header_or_footer in headers_or_footers:
            paragraphs.extend(header_or_footer.paragraphs)
            paragraphs.extend(self.__load_tables(header_or_footer.tables))
        return paragraphs

    def __is_text_skipped(self, text):
        text = text.replace(" ", "")
        return text in self.excludes or text.isdigit()

    def __preprocess(self, to_translate_dict):
        processed = {}

        processed.update(to_translate_dict)

        # 将key, value中的:替换为\\: 防止json解析错误, 并去除原始的key
        # for key, value in to_translate_dict.items():
        #     processed[key.replace(":", "\\:")] = value.replace(":", "\\:")

        # 使用术语表预处理文本, 如果术语表中有对应的翻译则直接使用, 替换结果为dict的value
        for key in processed:
            for term_key, term_value in self.terms.items():
                if term_key in key:
                    processed[key] = processed[key].replace(term_key, term_value)

        return processed

    def __split_dict_by_token_limit(self, original_dict, max_token_limit):
        current_dict = {}
        dicts = []
        current_token_count = 2  # Start with 2 for '{}'

        for key, value in original_dict.items():
            key_str = json.dumps({key: value})
            key_token_count = len(key_str)
            if current_token_count + key_token_count > max_token_limit:
                dicts.append(current_dict)
                current_dict = {}
                current_token_count = 2  # Reset for '{}'

            current_dict[key] = value
            current_token_count += key_token_count

        if current_dict:
            dicts.append(current_dict)

        return dicts

    def translate(self, file):
        start = time.time()
        self.debug_file_path = file.replace(".docx", f"-debug-{time.time()}.txt")

        # 复制文件
        translated_file = file.replace(".docx", "-translated.docx")
        self._copy_file(file, translated_file)

        doc = Document(translated_file)

        paragraphs = []
        # 读取所有段落
        headers = [section.header for section in doc.sections]
        paragraphs.extend(self.__load_headers_or_footers(headers))
        footers = [section.footer for section in doc.sections]
        paragraphs.extend(self.__load_headers_or_footers(footers))
        shapes = []
        for shape in doc.inline_shapes:
            shapes.append(shape)
        paragraphs.extend(shapes)
        paragraphs.extend(doc.paragraphs)
        paragraphs.extend(self.__load_tables(doc.tables))

        # 获取所有段落文本
        texts = set()
        for paragraph in paragraphs:
            texts.add(paragraph.text)

        # 分离中英文文本
        to_translate_texts = []
        for text in texts:
            if not self.__is_text_skipped(text):
                if self.to_CN and not su.has_chinese(
                    text
                ):  # 翻译成中文，只翻译英文文本
                    to_translate_texts.append(text)
                elif not self.to_CN and su.has_chinese(
                    text
                ):  # 翻译成英文，只翻译中文文本
                    to_translate_texts.append(text)

        # 只翻译前30个
        # to_translate_texts = to_translate_texts[:30]

        print(f"待翻译文本数量: {len(to_translate_texts)}")
        for index, text in enumerate(to_translate_texts):
            print(f"{index}: {text}")

        if len(to_translate_texts) == 0:
            print("------------翻译已经全部完成------------")
            return

        # 翻译
        translated_dict = {}
        # 分割dict
        to_translate_dicts = self.__split_dict_by_token_limit(
            {text: text for text in to_translate_texts}, 8000
        )
        print(f"分割后的dict数量: {len(to_translate_dicts)}")
        for to_translate_dict in to_translate_dicts:
            to_translate_dict = self.__preprocess(to_translate_dict)
            translated_dict.update(self.translator.translate(to_translate_dict))
            # translated_dict.update(to_translate_dict)

            print(f"当前翻译段落数量: {len(to_translate_dict)}")
            print(f"已翻译: {len(translated_dict)} / {len(to_translate_texts)}")

        # 写入log
        if self.debug_mode:
            with open(self.debug_file_path, "w", encoding="utf-8") as debug_file:
                for key, value in translated_dict.items():
                    debug_file.write(f"原文: {key}\n\n")
                    debug_file.write(f"译文: {value}\n")
                    debug_file.write(
                        "--------------------------------------------------------------------------------------\n"
                    )

        # 更新段落文本
        for paragraph in paragraphs:
            if paragraph.text in translated_dict:
                paragraph.text = translated_dict[paragraph.text]
        pass

        # 保存文件
        doc.save(translated_file)

        end = time.time()
        print(f"翻译完成，用时: {end - start:.2f} 秒")


if __name__ == "__main__":
    translator = DocTranslator(False)
    translator.translate(
        "ICR小鼠灌胃给予sbk002及硫酸氢氯吡格雷原料药-单次给药毒性试验-报告-正文-translated-translated.docx"
    )
