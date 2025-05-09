import os
import openai
from typing import Dict, Optional
from app.core.config import settings

class PromptsBuilder:
    """
    产品摘要和对话prompt的核心类。
    """
    def __init__(
            self, 
            api_key: str = None, 
            base_url: str = None, 
            model: str = None
        ):
        
        self.api_key = api_key or settings.SUMMARY_API_KEY
        self.base_url = base_url or settings.SUMMARY_BASE_URL
        self.model = model or settings.SUMMARY_MODEL

    def summarize_product(
            self, 
            product_info: str,  
            temperature: float = 0.7
        ):
        
        prompt = f"""
        Instruction: As a professional product analyst, please generate a structured summary based on the following text, which should be precise, concise, and exclude secondary information.
        Context:
        {product_info}
        Required Output Format:
        Product Name:
        2. Core functions (no more than 3 items) :
        3. Unique Selling Point :
        4. Target Users/Scenarios:
        5. Key technical parameters (if any) :
        6. Summary (within 50 words) :

        Additional requirements:
        - Use objective statements and avoid subjective modifiers;
        Technical terms should be accompanied by brief explanations;
        Output the summary directly, and do not say anything else.    
        """

        client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise e

    def select_role_prompt(
        self,
        product_summary,
        user_info,
    ):
        """
        user_info:
        # user_id,
        # nick_name,
        # mobile_phone,
        # username,
        # country,
        # last_name=None,
        # age=None,
        # gender=None,
        # interested=None,
        # email=None,
        # hobbies=None,
        # job=None,
        # income=None,
        # remark=None
        """

        # teenage
        if int(user_info.get('age', '')) < 18:
            return "You are a youthful and energetic product recommender, good at communicating with teenagers in youthful language, and enjoy expressing yourself with popular words and humor."
        # high income
        if int(user_info.get('income', '')) > 20000:
            return "You are a professional high-end product consultant, good at communicating with high-income users in professional terms, and pay attention to product performance and quality."
        # female
        if user_info.get('gender', '') == "female":
            return "You are a gentle and meticulous best friend type of consultant, good at understanding the needs of female users, and pay attention to emotional resonance and quality of life."
        # hobbies==sport
        if "sports" in user_info.get('hobbies', ''):
            return "You are a health and lifestyle expert who loves sports. You are good at communicating with users in positive language and recommending products suitable for sports scenarios."
        # IT
        if "engineer" in user_info.get('job', '').lower() or "developer" in user_info.get('job', '').lower() or "IT" in user_info.get('job', ''):
            return "You are a product expert who understands technology and can introduce the technical highlights of the product in a professional yet accessible way."
        # single user
        if user_info.get('interested', '') == "single":
            return "You are a considerate life consultant, good at recommending products that enhance the quality of life for single users."
        # default
        return None 

    def build_dialog_prompt(
        self,
        product_summary: str,
        user_info: Dict[str, str],
        role_system_prompt: Optional[str] = None
    ):
        
        default_prompt = self.default_role_prompt(user_info)
        
        if role_system_prompt:
            role_system_prompt = f"{default_prompt}\n\n# Advanced Role Settings:\n{role_system_prompt}"
        else:
            role_system_prompt = default_prompt
            
        # user info
        user_info_str = "\n".join([
            f"- USER_ID: {user_info.get('user_id', '')}",
            f"- NICK_NAME: {user_info.get('nick_name', '')}",
            f"- MOBILE_PHONE: {user_info.get('mobile_phone', '')}",
            f"- USERNAME: {user_info.get('username', '')}",
            f"- COUNTRY: {user_info.get('country', '')}",
            f"- LAST_NAME: {user_info.get('last_name', '')}",
            f"- AGE: {user_info.get('age', '')}",
            f"- GENDER: {user_info.get('gender', '')}",
            f"- INTERESTED: {user_info.get('interested', '')}",
            f"- EMAIL: {user_info.get('email', '')}",
            f"- HOBBIES: {user_info.get('hobbies', '')}",
            f"- JOB: {user_info.get('job', '')}",
            f"- INCOME: {user_info.get('income', '')}",
            f"- REMARK: {user_info.get('remark', '')}"
        ])
            
        # final prompt
        final_prompt = f"""{role_system_prompt}\n\n# User information:\n{user_info_str}\n\n# Product summary:\n{product_summary}
        """
        return final_prompt


    @staticmethod
    def default_role_prompt(user_info: Dict[str, str]) -> str:
        template_path = os.path.join(os.path.dirname(__file__), "prompt_template", "system_default.txt")
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
        # keys = ["user_id", "nick_name", "mobile_phone", "username", "country", "last_name", "age", "gender", "interested", "email", "hobbies", "job", "income", "remark"]
        # for k in keys:
        #     user_info.setdefault(k, "")
        return template.format(**user_info)
