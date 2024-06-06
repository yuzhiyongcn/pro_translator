import fitz  # PyMuPDF
import winreg


def translate(text):
    # 你的翻译逻辑或API调用
    # 这里是假设一个简单的直接替换
    # 实际使用中你可以调用你的翻译API
    translated_text = text.replace("Title Page", "标题页")
    return translated_text


def translate_pdf(pdf_path, output_path):
    document = fitz.open(pdf_path)

    for page_num in range(len(document)):
        page = document[page_num]
        text_instances = page.get_text("dict")

        for block in text_instances["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        original_text = span["text"]
                        translated_text = translate(original_text)
                        span["text"] = "标题"  # 修改文本

        # 清除当前页内容

    document.save(output_path)
    document.close()


def extract_unique_fonts_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    font_names = set()  # 用于存储唯一的字体名称

    for page_num in range(len(document)):
        page = document[page_num]
        text_instances = page.get_text("dict")

        for block in text_instances["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_name = span["font"]
                        font_names.add(font_name)

    document.close()
    return font_names


def list_installed_fonts():
    installed_fonts = []
    try:
        # 打开字体注册表项
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts",
        ) as reg_key:
            index = 0
            while True:
                try:
                    # 获取字体名称和对应的字体文件路径
                    font_value = winreg.EnumValue(reg_key, index)
                    font_name = font_value[0]  # 字体名称
                    font_path = font_value[1]  # 字体文件路径
                    installed_fonts.append((font_name, font_path))
                    index += 1
                except OSError:
                    # 如果没有更多的字体，则跳出循环
                    break
    except FileNotFoundError:
        # 如果注册表项不存在，则输出错误信息
        print("Error: Fonts registry key not found.")

    return installed_fonts


def check_missing_fonts(fonts):
    missing_fonts = []
    for font in fonts:
        try:
            # 尝试打开字体注册表项
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts",
            ) as reg_key:
                # 从注册表中获取字体文件路径
                font_path, _ = winreg.QueryValueEx(reg_key, font)
                # 如果字体文件路径为空，则说明字体不存在
                if not font_path:
                    missing_fonts.append(font)
        except FileNotFoundError:
            # 如果注册表项不存在，则说明字体不存在
            missing_fonts.append(font)
    return missing_fonts


if __name__ == "__main__":
    input_pdf_path = "NSR_T103508-7_PH-42754_DRF dog.pdf"  # 输入PDF文件路径
    output_pdf_path = "translated_output.pdf"  # 输出翻译后PDF文件路径

    translate_pdf(input_pdf_path, output_pdf_path)
    # print(extract_unique_fonts_from_pdf(input_pdf_path))

    # fonts_to_check = {
    #     "CourierNew,Bold",
    #     "Times-Roman",
    #     "Helvetica",
    #     "Times-Bold",
    #     "ArialMT",
    #     "Times-BoldItalic",
    #     "Symbol",
    #     "Arial,Bold",
    #     "Helvetica-Bold",
    #     "Calibri",
    #     "Arial",
    #     "CourierNew",
    #     "TimesNewRoman",
    #     "Times-Italic",
    #     "TimesNewRoman,Bold",
    #     "PathData",
    # }

    # missing_fonts = check_missing_fonts(fonts_to_check)

    # # 打印缺少的字体
    # if missing_fonts:
    #     print("系统缺少以下字体:")
    #     for font in missing_fonts:
    #         print(font)
    # else:
    #     print("系统已安装所有字体")

    # installed_fonts = list_installed_fonts()

    # # 打印已安装的字体信息
    # if installed_fonts:
    #     print("已安装的字体:")
    #     for font_name, font_path in installed_fonts:
    #         print(f"{font_name}: {font_path}")
    # else:
    #     print("系统中未安装任何字体.")
