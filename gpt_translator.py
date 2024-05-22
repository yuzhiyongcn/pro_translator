from openai import OpenAI
import os
import ast


class GPTTranslator:
    def __init__(self, terminology=None, to_CN=True):
        self.model = "gpt-4o"
        self.to_CN = to_CN
        self.terminology = terminology
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        self.system_prompt = """
        You are a professional translator.
        The translation should be professional, complete, and must not omit any words.
        If a string contains numbers or units of measure e.g. length, volume, capacity, density, etc, try to translate what you can, but it's okay to leave the numbers or units of measure in the original language.
        If a string contains spaces, tabs, punctuation, or special characters, try to preserve them in the translation.
        Do not remove spaces, tabs in the string. e.g. "   1.    hello  ", you can reply with "1.    你好".
        Multiple adjacent 'Ä's are translated into the same length of '-', for example, 'ÄÄÄ' is translated into '---'.
        If a string contains '\t' or '\n', try to preserve them in the translation.
        When I ask you for a translation, please reply with the translated text only.
        If you find there is nothing to translate, just reply with the original text.
        """

    def __get_user_prompt(self, text):
        user_prompt_CN = "Translate the following English text to Chinese:"
        user_prompt_EN = "Translate the following Chinese text to English:"
        return user_prompt_CN + text if self.to_CN else user_prompt_EN + text

    def __create_system_instruction(self, terminology):
        terms = ", ".join([f"'{k}' -> '{v}'" for k, v in terminology.items()])
        return f"Please use the following translations for specific terms: {terms}."

    def translate(self, text):
        if (
            isinstance(text, list)
            and len(text) == 0
            or isinstance(text, str)
            and text.strip() == ""
        ):
            return text

        system_message = (
            self.system_prompt + self.__create_system_instruction(self.terminology)
            if self.terminology and len(self.terminology) > 0
            else self.system_prompt
        )
        messages = [
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": self.__get_user_prompt(
                    repr(text) if isinstance(text, list) else text
                ),
            },
        ]

        # 使用新的 API 调用
        response = self.client.chat.completions.create(
            model=self.model,  # 使用合适的 GPT 模型
            messages=messages,
            max_tokens=2048,  # 确定生成的响应能适配提供的标记数量
        )

        msg = response.choices[0].message.content
        if " -> " in msg:
            msg = msg.split(" -> ")[1]
        return ast.literal_eval(msg) if isinstance(text, list) else msg


if __name__ == "__main__":
    translator = GPTTranslator({"understood": "知晓"}, True)
    text = "	3.	Conclusion"
    print(text)
    print(translator.translate(text))
