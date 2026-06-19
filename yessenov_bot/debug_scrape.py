import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

urls = [
    "https://yessenovfoundation.org/about-us/programs/science/yessenov-scholarship/stipendiya-im-akademika-sh-esenova-2025/",
    "https://yessenovfoundation.org/about-us/programs/science/research-internships/programma-nauchnyh-stazhirovok-v-laboratoriyah-mira-2025/",
    "https://yessenovfoundation.org/about-us/programs/science/travel-grants/",
    "https://yessenovfoundation.org/about-us/programs/science/orleu/",
    "https://yessenovfoundation.org/about-us/programs/resources/yessenov-launch-pad/",
]

with open("debug_scrape_output.txt", "w", encoding="utf-8") as out:
    for url in urls:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "meta"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        clean = "\n".join(lines)
        out.write(f"=== {url} ===\n")
        out.write(f"Total chars: {len(clean)}\n")
        out.write(clean + "\n\n")
        print(f"Scraped {url} -> {len(clean)} chars")

print("Done. Written to debug_scrape_output.txt")
