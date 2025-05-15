import os
import openai
from ragflow_sdk import RAGFlow
from typing import Dict, Optional
from app.core.config import settings

class PromptsBuilder:
    """
    产品摘要和对话prompt的核心类。
    """
    def __init__(
            self, 
            summary_api_key: str = None, 
            summary_base_url: str = None, 
            summary_model: str = None,
            ragflow_api_key : str = None,
            ragflow_base_url : str = None,
            ragflow_dataset_id : str = None
        ):
        # api key for summary product info
        self.summary_api_key = summary_api_key or settings.SUMMARY_API_KEY
        self.summary_base_url = summary_base_url or settings.SUMMARY_BASE_URL
        self.summary_model = summary_model or settings.SUMMARY_MODEL
        # api key for get {rag_context} from ragflow
        self.ragflow_api_key = ragflow_api_key or settings.RAGFLOW_API_KEY
        self.ragflow_base_url = ragflow_base_url or settings.RAGFLOW_BASE_URL
        self.ragflow_dataset_id = ragflow_dataset_id or settings.RAGFLOW_DATASET_ID

        #init ragflow
        self.ragflow = RAGFlow(api_key=self.ragflow_api_key, base_url=self.ragflow_base_url)

    def summarize_product(
            self, 
            product_info: str,  
            temperature: float = 0.7
        ):
        template_path = os.path.join(os.path.dirname(__file__), "prompt_template", "summary_default.txt")
        with open(template_path, "r", encoding="utf-8") as f:
            summary_prompt = f.read()
        summary_prompt = summary_prompt.format(product_info=product_info)

        client = openai.OpenAI(
            api_key=self.summary_api_key,
            base_url=self.summary_base_url,
        )
        try:
            response = client.chat.completions.create(
                model=self.summary_model,
                messages=[{"role": "user", "content": summary_prompt}],
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise e

    def get_rag_context(
            self,
            query: str,
            top_k: int = 5
        ):
        try:
            chunks = self.ragflow.retrieve(
                question=query,
                dataset_ids=[self.ragflow_dataset_id],
                document_ids=None,
                page=1,
                page_size=top_k,
                similarity_threshold=0.5,
                vector_similarity_weight=0.4,
                top_k=top_k,
                keyword=True
                )
            
            rag_context = "\n".join([c.content for c in chunks])
            return rag_context
        except Exception as e:
            raise e

    def get_all_roles_list(self):
        roles_dir = os.path.join(os.path.dirname(__file__), "prompt_template", "roles")
        roles_list= []
        for filename in os.listdir(roles_dir):
            if filename.endswith('.txt'):
                role_name = filename[:-4]
                roles_list.append(role_name)
        return roles_list

    def select_role_prompt(
        self,
        role_name=None
    ):
        if not role_name:
            role_name = 'default'
        role_prompt_path = os.path.join(os.path.dirname(__file__), "prompt_template", "roles", f"{role_name}.txt")
        if os.path.exists(role_prompt_path):
            with open(role_prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return "You are a person with a neutral personality."


    def build_dialog_prompt(
        self,
        product_summary: str,
        user_info: Dict[str, str],
        user_query: str,
        role_system_prompt: Optional[str] = None
    ):
        # role prompt
        role_system_prompt = role_system_prompt or '\n'
        # user info prompt
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
        # rag prompt
        rag_context = self.get_rag_context(query=user_query, top_k=3)
        rag_context = rag_context or '\n'

        final_prompt = self.default_role_prompt(
            user_info = user_info,
            role_system_prompt = role_system_prompt,
            user_info_str = user_info_str,
            product_summary = product_summary,
            rag_context = rag_context
            )
        return final_prompt


    @staticmethod
    def default_role_prompt(
        user_info: Dict[str, str],
        role_system_prompt: str,
        user_info_str: str,
        product_summary: str,
        rag_context: str
        ) -> str:
        template_path = os.path.join(os.path.dirname(__file__), "prompt_template", "system_default.txt")
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
        format_dict = dict(user_info)
        format_dict['role_system_prompt'] = role_system_prompt
        format_dict['user_info_str'] = user_info_str
        format_dict['product_summary'] = product_summary
        format_dict['rag_context'] = rag_context
        return template.format(**format_dict)
        
