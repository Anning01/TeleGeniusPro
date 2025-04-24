import deepl

from app.core.config import settings


class Translator:

    def get_available_key(self):
        """
        Obtain an available translation key.
        return:
            TranslationKeys: An available TranslationKeys object. If there is no available key, it returns None
        """
        return settings.DEEPL_API_KEY

    def translate(
        self, text: str, source_lang: str = None, target_lang: str = settings.LANGUAGE
    ):
        """
        Perform the translation operation, use the available key and switch automatically.
        parameter:
            text (str): The text to be translated
            name (str): The name of the translation record
            source_lang (str, optional): Source language code, default is None (automatic detection)
            target_lang (str, optional): Target language code, default is "zh" (Chinese)
        return:
            dict: Translation result, including the translated text, the detected source language, the number of charged characters, etc
        throw:
            Exception: If there is no available key or other errors occur during the translation process
        """
        while True:
            key = self.get_available_key()
            if not key:
                raise Exception("No available translation key")

            deepl_client = deepl.DeepLClient(key)
            try:
                result = deepl_client.translate_text(
                    text, source_lang=source_lang, target_lang=target_lang
                )

                return result

            except Exception as e:
                raise e
