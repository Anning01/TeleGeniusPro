import deepl

from app.core.config import settings


class Translator:
    """
    一个翻译类，用于管理翻译密钥并执行翻译操作。
    支持自动切换密钥，并在翻译后更新数据库记录。
    """

    def get_available_key(self):
        """
        获取一个可用的翻译密钥。

        返回:
            TranslationKeys: 一个可用的 TranslationKeys 对象，如果没有可用密钥则返回 None
        """
        return settings.DEEPL_API_KEY

    def translate(
        self, text: str, source_lang: str = None, target_lang: str = settings.LANGUAGE
    ):
        """
        执行翻译操作，使用可用的密钥并自动切换。

        参数:
            text (str): 要翻译的文本
            name (str): 翻译记录的名称
            source_lang (str, optional): 源语言代码，默认为 None（自动检测）
            target_lang (str, optional): 目标语言代码，默认为 "zh"（中文）

        返回:
            dict: 翻译结果，包含翻译后的文本、检测到的源语言、计费字符数等

        抛出:
            Exception: 如果没有可用密钥或翻译过程中出现其他错误
        """
        while True:
            key = self.get_available_key()
            if not key:
                raise Exception("No available translation key")

            deepl_client = deepl.DeepLClient(key)
            try:
                # 执行翻译
                result = deepl_client.translate_text(
                    text, source_lang=source_lang, target_lang=target_lang
                )


                return result

            except Exception as e:
                raise e


if __name__ == "__main__":
    try:
        result = Translator().translate(
            text="Hello, world!", target_lang="zh"  # 替换为实际的用户ID
        )
        print(
            result
        )  # 输出类似 {'text': '你好，世界', 'detected_source_lang': 'EN', 'billed_characters': 13, 'model_type_used': None}
    except Exception as e:
        print(f"翻译失败: {e}")
