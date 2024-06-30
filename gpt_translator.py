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
        Your translated text should be in the value of key-value pair, do not change the key.
        If i provide '{"早上好中国":"good morning中国", "你好":"你好"}', you should return '{"早上好中国":"good morning China", "你好":"hello"}".
        Do not explain, just return json string without ```json```. e.g. {'key': 'value'}
        Please ensure that your output is a valid JSON string that can be correctly parsed.
        """
        self.gpt.set_system_prompt(system_prompt)

    def translate(self, dic):
        json_str = self.gpt.query(json.dumps(dic))
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            print(f"解析成json Object失败: \n{json_str}\n")
            json_str = self.to_json(json_str)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                print(f"再次尝试解析成json Object失败: \n{json_str}\n")
                return {}

    def to_json(self, s):
        json_gpt = GPTWrapper()
        json_gpt.set_system_prompt(
            "请将文本修复为正确的 JSON 格式. Do not explain, just return json string without ```json```. e.g. {'key': 'value'}"
        )
        return json_gpt.query(s)


if __name__ == "__main__":
    translator = GPTTranslator(False)
    text = {"中 国": "中 国", "你好! Mike": "你好! Mike"}
    print(text)
    print(translator.translate(text))
