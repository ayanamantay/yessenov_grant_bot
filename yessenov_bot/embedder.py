import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

EMBED_URL = os.getenv("EMBED_URL")
EMBED_KEY = os.getenv("EMBED_KEY")
EMBED_MODEL = os.getenv("EMBED_MODEL")

CHUNK_SIZE = 800
OVERLAP = 100


def get_embedding(text: str) -> list:
    response = requests.post(
        EMBED_URL,
        headers={"Authorization": f"Bearer {EMBED_KEY}", "Content-Type": "application/json"},
        json={"model": EMBED_MODEL, "input": text},
        timeout=30
    )
    response.raise_for_status()
    return response.json()["data"][0]["embedding"]


def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def main():
    print("Reading knowledge_base.txt...")
    with open("knowledge_base.txt", "r", encoding="utf-8") as f:
        text = f.read()

    chunks = split_into_chunks(text)
    result = [{"text": chunk} for chunk in chunks]

    with open("chunks.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    print(f"Done! {len(result)} chunks saved to chunks.json")


if __name__ == "__main__":
    main()
