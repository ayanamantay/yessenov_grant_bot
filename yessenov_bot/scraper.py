from playwright.sync_api import sync_playwright
import time

PAGES = [
    "https://yessenovfoundation.org",
    "https://yessenovfoundation.org/about-us/mission-and-reports/",
    "https://yessenovfoundation.org/about-us/programs/",
    "https://yessenovfoundation.org/about-us/programs/science/research-internships/",
    "https://yessenovfoundation.org/about-us/programs/science/research-internships/programma-nauchnyh-stazhirovok-v-laboratoriyah-mira-2025/",
    "https://yessenovfoundation.org/about-us/programs/science/yessenov-scholarship/",
    "https://yessenovfoundation.org/about-us/programs/science/yessenov-scholarship/stipendiya-im-akademika-sh-esenova-2025/",
    "https://yessenovfoundation.org/about-us/programs/knowledge/english-language-program/",
    "https://yessenovfoundation.org/about-us/programs/resources/yessenov-data-lab/",
    "https://yessenovfoundation.org/about-us/programs/resources/yessenov-launch-pad/",
    "https://yessenovfoundation.org/about-us/programs/resources/internships-in-it-startups/",
    "https://yessenovfoundation.org/about-us/programs/science/graduate-studies/",
    "https://yessenovfoundation.org/about-us/programs/science/travel-grants/",
    "https://yessenovfoundation.org/about-us/programs/knowledge/chess/",
    "https://yessenovfoundation.org/about-us/programs/science/orleu/",
    "https://yessenovfoundation.org/about-us/galimzhan-yessenov/",
    "https://yessenovfoundation.org/category/novosti/novosti-fonda/?y=2026",
    "https://yessenovfoundation.org/category/novosti/istorii-uspeha/",
]


def scrape_with_playwright():
    all_text = ""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for url in PAGES:
            print(f"Scraping: {url}")
            try:
                page.goto(url, timeout=15000)
                page.wait_for_timeout(3000)
                page.evaluate("""
                    document.querySelectorAll('nav,footer,header,script,style').forEach(e => e.remove())
                """)
                text = page.inner_text("body")
                lines = [l.strip() for l in text.splitlines() if l.strip()]
                clean = "\n".join(lines)
                all_text += f"\n=== PAGE: {url} ===\n{clean}\n"
                print(f"  Collected {len(clean)} characters")
            except Exception as e:
                print(f"  ERROR: {e}")
            time.sleep(1)
        browser.close()
    return all_text


text = scrape_with_playwright()
with open("knowledge_base.txt", "w", encoding="utf-8") as f:
    f.write(text)
print(f"\nDone! Total: {len(text)} characters saved to knowledge_base.txt")
