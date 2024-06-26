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
        The translation should be professional, complete, and must not omit any words.
        If a string contains numbers or units of measure e.g. length, volume, capacity, density, etc, try to translate what you can, but it's okay to leave the numbers or units of measure in the original language.
        If a string contains spaces, tabs, punctuation, or special characters, try to preserve them in the translation.
        Do not remove any spaces or tabs before, between, or after the strings.
        If a string contains '\t' or '\n', try to preserve them in the translation.
        I will provide you text in json format, you should translate and return pure json format.
        I may provide string mixed with English and Chinese, you should translate them to the target language.
        If i provide '{"中国good morning":"", "你好":""}', you should return '{"中国good morning":"good morning China", "你好":"hello"}".
        Do not explain, just return json string without ```json``` or any other characters.
        """
        self.gpt.set_system_prompt(system_prompt)

    def translate(self, dic):
        json_str = self.gpt.query(json.dumps(dic))
        return ast.literal_eval(json_str)


if __name__ == "__main__":
    translator = GPTTranslator(False)
    text = {"中 国": "", "你好! Mike": ""}
    print(text)
    print(translator.translate(text))
