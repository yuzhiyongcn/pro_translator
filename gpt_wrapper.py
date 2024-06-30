from openai import OpenAI
import os


class GPTWrapper:
    def __init__(self, model="gpt-4o"):
        self.model = model
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        self.system_prompt = ""

    def set_system_prompt(self, prompt):
        self.system_prompt = prompt

    def query(self, text):
        messages = [
            {
                "role": "system",
                "content": self.system_prompt,
            },
            {
                "role": "user",
                "content": text,
            },
        ]

        response = self.client.chat.completions.create(
            model=self.model,  # 使用合适的 GPT 模型
            messages=messages,
            max_tokens=4096,  # 确定生成的响应能适配提供的标记数量
        )

        return response.choices[0].message.content.strip()
