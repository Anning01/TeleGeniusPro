import openai

from app.prompts.base import get_prompt


class Chat:
    """
    聊天类，用于模拟聊天行为。

    Attributes:
        history (list): 聊天记录列表
    Methods:
        say(message: str) -> str: 发送消息
        listen() -> str: 监听消息
    """

    history = []

    def __init__(self, history: list, user_meta: dict):
        self.history = []
        self.say({"role": "system", "content": get_prompt(**user_meta)})
        self.history += history

    def say(self, message):
        self.history.append(message)
        return message

    def listen(self):
        return self.history[-1] if self.history else None

    def chat_with_openai(self):
        try:
            # 创建 OpenAI 客户端实例
            client = openai.OpenAI(
                api_key="ollama",
                # api_key="sk-WwaTeLS5QwO02nbvEKkyHNjtCWZdVsF9izgcbESBAhofSVOf",
                # base_url="https://api.moonshot.cn/v1"
                base_url="http://localhost:11434/v1",
            )
            # 调用新版本的聊天完成 API
            response = client.chat.completions.create(
                model="gemma3:27b-it-q4_K_M",
                messages=self.history,
            )
            result = response.choices[0].message.content

            self.say({"role": "assistant", "content": result})
            return result
        except Exception as e:
            raise e
