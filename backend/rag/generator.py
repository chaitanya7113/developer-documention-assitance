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

Answer the user's question using the documentation context below.

Rules:
1. Read all the provided context before answering.
2. If the context contains relevant information, answer using that information.
3. If the user asks where a function is documented, use the file and section
   information provided in the context.
4. Do not require the context to contain the exact wording of the question.
5. If the context genuinely does not contain enough information, say:
   "I couldn't find the answer in the provided documentation."
6. Do not invent documentation locations, file paths, or section names.

Documentation Context:
<context>
{context}
</context>

User Question:
{question}

Answer:
"""

    response = llm.invoke(prompt)
    answer = response.content

    print("LLM raw answer:", repr(answer))

    return answer
