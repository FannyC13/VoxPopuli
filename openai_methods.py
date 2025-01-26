from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

model = "gpt-4o-mini"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

sys_prompt = "Hello blabla"

def categorize(user_prompt, system_prompt=sys_prompt, model="gpt-4o"):
    """Translates a user prompt to FALC using a GPT-3.5-turbo fine-tuned model.

    Args : user_prompt (str) : The text in 'classic' French to be transcripted.
           system_prompt (str) : The system prompt to be used in the completion.
           model (str) : The model used for the completion.

    Returns : message_content (str) : The FALC transcripted text.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model,
        temperature = 0.2
    )

    message_content = chat_completion.choices[0].message.content
    return message_content.replace('\n', '<br>')