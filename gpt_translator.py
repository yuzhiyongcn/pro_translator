import ast
import json
from gpt_wrapper import GPTWrapper


class GPTTranslator:
    def __init__(self, to_CN=True):
        self.gpt = GPTWrapper()
        self.to_CN = to_CN
        system_prompt = "You are a professional translator."
        system_prompt += (
            "Please translate English to Chinese."
            if to_CN
            else "Please translate Chinese to English."
        )
        system_prompt += """
        翻译需要专业, 完整, 不遗漏.
        数字和度量衡单位不需要翻译, 保留原样, 比如5g 40ml 都保留原样.
        字符串的首尾空格可以去除, 但是字符串中间的空格, 或者换行符等不能去除.
        我提供的文本将是多个短句中间用'[#]'分割的字符串, 你需要将每个短句翻译成目标语言.比如"Hello[#]World"翻译成"你好[#]世界".
        如果我提供的字符串中包含英文和中文, 如果要求你翻译成中文,你需要将其中的英文翻译成中文, 尽量保留中文, 但是要保证语句通顺. 如果要求你翻译成英语, 则需要保留英文的基础上翻译成英文.
        不需要解释, 只需要返回翻译后的字符串, 多个短句之间用'[#]'分割.
        """
        self.gpt.set_system_prompt(system_prompt)

    def translate(self, source_text):
        source_count = len(source_text.split("[#]"))
        result_text = self.gpt.query(source_text)
        result_count = len(result_text.split("[#]"))
        if source_count != result_count:
            print(
                f"翻译前后数量不一致, 翻译前数量: {source_count}, 翻译后数量: {result_count}"
            )
            print(f"翻译前: {source_text}")
            print(f"翻译后: {result_text}")
            return source_text
        return result_text


if __name__ == "__main__":
    translator = GPTTranslator(False)
    text = "Supplier：成都施贝康生物医药科技Co., Ltd.。[#]samplescollect量[#]4.8.   Animal Selection        14[#]地址：成都New & Hi-tech Industrial Development Zone西芯大道17号；[#]检疫和适应[#]beagle dog分别经口给予30 mg/只 sbk002片和75 mg/只硫酸氢氯吡格雷片后，与in vivo暴露量related的parameterCmax分别为39.60 ± 18.66 ng/mL和75.65 ± 46.61 ng/mL（Cmax之比为1.00 : 1.91），AUC0-24h分别为127.90 ± 53.28 h*ng/mL和139.23 ± 60.21 h*ng/mL（AUC0-24h之比为1.00 : 1.09），time to reach maximumTmax分别为0.75 ± 0.35 h和0.63 ± 0.40 h，T1/2分别为8.47 ± 2.59 h和7.53 ± 2.71 h。"
    text = "white的fox"
    print(text)
    print(translator.translate(text))
