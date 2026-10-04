import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=OPENAI_API_KEY
)


def generate_answer(question, context):
    prompt = f"""
You are a developer documentation assistant.

Answer the user's question using only the provided documentation context.

If the answer is not present in the context, say:
"I couldn't find the answer in the provided documentation."

Documentation Context:
{context}

User Question:
{question}

Answer:
"""

    response = llm.invoke(prompt)

    return response.content