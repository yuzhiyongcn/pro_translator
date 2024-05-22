import fitz  # PyMuPDF


def translate(text):
    # 你的翻译逻辑或API调用
    # 这里是假设一个简单的直接替换
    # 实际使用中你可以调用你的翻译API
    translated_text = text.replace("Title Page", "标题页")
    return translated_text


def translate_pdf(input_pdf_path, output_pdf_path):
    # 打开PDF文件
    pdf_document = fitz.open(input_pdf_path)

    # 遍历每一页
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        text_dict = page.get_text("dict")

        # 遍历每一个文本块
        for block in text_dict["blocks"]:
            if "lines" in block:  # 确保块中有文本行
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"]
                        translated_text = translate(text)

                        # 获取文本的位置
                        rect = fitz.Rect(span["bbox"])

                        # 删除原有文本
                        page.add_redact_annot(
                            rect, fill=(1, 1, 1)
                        )  # 填充白色覆盖原有文本
                        page.apply_redactions()  # 应用覆盖

                        # 插入翻译后的文本
                        page.insert_text(
                            rect.tl,
                            translated_text,
                            fontsize=span["size"],
                            color=(0, 0, 0),
                        )

    # 保存翻译后的PDF
    pdf_document.save(output_pdf_path)
    pdf_document.close()


if __name__ == "__main__":
    input_pdf_path = "NSR_T103508-7_PH-42754_DRF dog.pdf"  # 输入PDF文件路径
    output_pdf_path = "translated_output.pdf"  # 输出翻译后PDF文件路径

    translate_pdf(input_pdf_path, output_pdf_path)
