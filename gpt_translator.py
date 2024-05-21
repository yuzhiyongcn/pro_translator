from openai import OpenAI
import os
import ast


class GPTTranslator:
    def __init__(self, terminology=None, to_CN=True):
        self.to_CN = to_CN
        self.terminology = terminology
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        self.system_prompt = "You are a professional translator.The translation should be professional, complete, and must not omit any words. Do not translate numbers, units of measure, e.g. length, volume, capacity, density, etc. When I ask you for a translation, please reply with the translated text only. If you find there is nothing to translate, just reply with the original text."

    def __get_user_prompt(self, text):
        user_prompt_CN = "Translate the following English text to Chinese:"
        user_prompt_EN = "Translate the following Chinese text to English:"
        return (
            user_prompt_CN + text
            if self.to_CN
            else user_prompt_EN + text
        )

    def __create_system_instruction(self, terminology):
        terms = ", ".join([f"'{k}' -> '{v}'" for k, v in terminology.items()])
        return f"Please use the following translations for specific terms: {terms}."

    def translate(self, text):
        if isinstance(text, list) and len(text) == 0 or isinstance(text, str) and text.strip() == "":
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
            model="gpt-4o",  # 使用合适的 GPT 模型
            messages=messages,
            max_tokens=2048,  # 确定生成的响应能适配提供的标记数量
        )

        msg = response.choices[0].message.content.strip()
        if ' -> ' in msg:
            msg = msg.split(' -> ')[1].strip()
        return ast.literal_eval(msg) if isinstance(text, list) else msg


if __name__ == "__main__":
    translator = GPTTranslator({"understood": "知晓"}, True)
    text = "Weigh 6 g of propylene glycol into a calibrated 100 mL container. After adding 3 g of Kolliphor® HS 15 and stirring until well mixed, add 51.8 mg of the test article. "
    print(translator.translate(text))
    # translator.to_CN = False
    # text = "一只白色的狐狸在森林里跑步."
    # resp = translator.translate(["皮球", "飞机", "彩色蝴蝶在花丛里飞"])
    # for r in resp:
    #     print(r)
