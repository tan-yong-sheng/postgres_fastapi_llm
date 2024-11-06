import os

import openai
from backend.schemas.message_schemas import RawMessageRequestSchema, RawAIMessageResponseSchema

# not perfect as it's just combining the last 5 messages, and feed it to the model...
# The model doesn't know it's previous conversation
def get_openai_response(messages: list[RawMessageRequestSchema], user_id: str) -> RawAIMessageResponseSchema:
    openai_client = openai.OpenAI(
                    api_key=os.getenv("OPENAI_API_KEY"), 
                    base_url=os.getenv("OPENAI_BASE_URL"))
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        top_p=1,
    )
    return response.choices[0].message
