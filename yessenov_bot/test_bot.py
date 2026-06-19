import os, sys, requests
sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
load_dotenv()
from rag import find_relevant, load_chunks

chunks = load_chunks()
print(f"Loaded {len(chunks)} chunks\n")

SYSTEM_PROMPT = """You are a precise assistant for the Shakhmardan Yessenov Foundation.

STRICT RULES - follow these exactly:
1. Answer ONLY using information from the provided context.
2. If context does not contain the answer - say EXACTLY:
   "В моих данных нет этой информации. Пожалуйста, проверьте актуальную информацию на yessenovfoundation.org"
3. NEVER invent or guess: dates, deadlines, amounts, requirements, names.
4. NEVER say a specific date or number unless it appears word-for-word in the context.
5. If asked about deadlines and context has no date - say you don't know the current deadline.
6. Reply in the same language the user writes - Russian, Kazakh, or English.
7. Be concise - maximum 5-6 sentences per answer.

If you are not 100% sure something is in the context - do not say it."""

LLM_URL = os.getenv("LLM_URL")
LLM_KEY = os.getenv("LLM_KEY")
LLM_MODEL = os.getenv("LLM_MODEL")

questions = [
    "Кто может подать заявку на стипендию Есенова?",
    "Какой размер стипендии Есенова?",
    "Каковы требования к кандидатам?",
    "Какой дедлайн подачи заявки?",
]

for q in questions:
    relevant = find_relevant(q, chunks, top_k=5)
    context_text = "\n\n---\n\n".join(relevant)
    resp = requests.post(
        LLM_URL,
        headers={"Authorization": f"Bearer {LLM_KEY}", "Content-Type": "application/json"},
        json={
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {q}"}
            ]
        },
        timeout=30
    )
    answer = resp.json()["choices"][0]["message"]["content"]
    print(f"Q: {q}")
    print(f"A: {answer}")
    print()
