import json
import numpy as np
import requests
import os
from dotenv import load_dotenv

load_dotenv()

EMBED_URL = os.getenv("EMBED_URL")
EMBED_KEY = os.getenv("EMBED_KEY")
EMBED_MODEL = os.getenv("EMBED_MODEL")


def load_chunks() -> list:
    with open("chunks.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_embedding(text: str) -> list:
    response = requests.post(
        EMBED_URL,
        headers={"Authorization": f"Bearer {EMBED_KEY}", "Content-Type": "application/json"},
        json={"model": EMBED_MODEL, "input": text},
        timeout=30
    )
    response.raise_for_status()
    return response.json()["data"][0]["embedding"]


def cosine_similarity(a: list, b: list) -> float:
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def find_relevant(question: str, chunks: list, top_k: int = 5) -> list:
    question_lower = question.lower()
    words = [w for w in question_lower.split() if len(w) > 2]

    scored = []
    for chunk in chunks:
        text_lower = chunk["text"].lower()
        score = 0
        if question_lower in text_lower:
            score += 10
        for word in words:
            if word in text_lower:
                score += 1
        grant_keywords = [
            "стипендия", "грант", "заявка", "программа", "есенов",
            "scholarship", "grant", "application", "program", "yessenov",
            "stipendiya", "требования", "условия", "дедлайн", "срок"
        ]
        for kw in grant_keywords:
            if kw in text_lower:
                score += 0.5
        if score > 0:
            scored.append((score, chunk["text"]))

    scored.sort(reverse=True)
    top = [text for _, text in scored[:top_k]]

    if not top:
        return [c["text"] for c in chunks[:3]]
    return top
