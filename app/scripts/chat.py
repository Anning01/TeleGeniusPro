import os
import openai


from app.prompts.base import get_prompt
from app.prompts.core import PromptsBuilder

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
    product_info = None
    product_summary = None
    role_prompt = None

    def __init__(self, history: list, user_meta: dict):
        self.history = []
        # TODO self.chat_rounds = int(len(history//2))
        self.user_meta = user_meta
        self.user_id = user_meta.get('user_id', '')
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.product_info_path = os.path.join(self.base_dir, '../prompts/docs/dataset.txt')
        self.product_summary_path = os.path.join(self.base_dir, f'../prompts/docs/product_summary_{self.user_id}.txt')
        # init PromptsBuilder
        self.prompts_builder = PromptsBuilder()
        # init product summary
        if Chat.product_info is None:
            with open(self.product_info_path, 'r', encoding="utf-8") as f:
                Chat.product_info = f.read()
        if Chat.product_summary is None:
            Chat.product_summary = self.prompts_builder.summarize_product(Chat.product_info)
            with open(self.product_summary_path, 'w', encoding="utf-8") as f:
                f.write(Chat.product_summary)
        # init role system prompt
        # TODO: 前端获取自定义角色性格提示词
        if Chat.role_prompt is None:
            Chat.role_prompt = self.prompts_builder.select_role_prompt()
        # init final prompt
        self.final_prompt = self.prompts_builder.build_dialog_prompt(
            product_summary=Chat.product_summary,
            user_info=self.user_meta,
            user_query= history[-1]['content'],
            role_system_prompt=Chat.role_prompt
        )
        # print(self.final_prompt)

        self.say({
            "role": "system", 
            # "content": get_prompt(**user_meta)
            "content": self.final_prompt
            })
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
                base_url="http://192.168.1.81:11434/v1",
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
