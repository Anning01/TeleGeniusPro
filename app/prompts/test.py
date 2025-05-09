
from core import PromptsBuilder

prompts_builder = PromptsBuilder()
user_info ={
    'age': '30', 
    'job': 'Information officer',
    'email': 'tcole@example.org', 
    'gender': 'male', 
    'income': '42984', 
    'remark': 'On campaign bring situation.', 
    'country': 'Singapore', 
    'hobbies': 'music', 
    'user_id': '282804', 
    'username': 'garciabarbara', 
    'last_name': 'Kent', 
    'nick_name': 'Patrick Roberson', 
    'interested': 'married', 
    'mobile_phone': '545-272-8984x9521'
    }

with open('docs/dataset.txt', 'r') as f:
    product_info = f.read()
product_summary = prompts_builder.summarize_product(product_info)
with open('docs/product_summary.txt', 'w') as f:
    f.write(product_summary)
role_prompt = prompts_builder.select_role_prompt(product_summary, user_info)

final_prompt = prompts_builder.build_dialog_prompt(
    product_summary=product_summary,
    user_info=user_info,
    role_system_prompt=role_prompt
)
print(final_prompt)
