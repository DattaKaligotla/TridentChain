import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import random
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

visited = set()
lock = None  # Will initialize with threading.Lock()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Mozilla/5.0 (X11; Linux x86_64)..."
]

def get_dynamic_headers():
    index = int(datetime.utcnow().timestamp()) % len(USER_AGENTS)
    return {
        "User-Agent": USER_AGENTS[index],
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

def extract_links(url):
    global visited
    with lock:
        if url in visited:
            return url, []

        visited.add(url)

    print(f"Scraping: {url}")
    try:
        resp = requests.get(url, headers=get_dynamic_headers(), timeout=10)
        if resp.status_code != 200:
            print(f"Failed ({resp.status_code}): {url}")
            return url, []

        soup = BeautifulSoup(resp.content, 'html.parser')
        links = [
            urljoin(url, a['href']) for a in soup.find_all('a', href=True)
            if "/suppliers/" in a['href']
        ]
        return url, links
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return url, []

def crawl_parallel(start_url, max_depth=5):
    from threading import Lock
    global lock
    lock = Lock()

    relationships = []
    queue = [(start_url, 0)]
    executor = ThreadPoolExecutor(max_workers=8)

    while queue:
        futures = {}
        for (url, level) in queue:
            if level < max_depth:
                futures[executor.submit(extract_links, url)] = (url, level)

        queue = []  # Clear queue for next level

        for future in as_completed(futures):
            parent_url, level = futures[future]
            try:
                _, children = future.result()
                for child_url in children:
                    relationships.append({'Parent': parent_url, 'Child': child_url})
                    queue.append((child_url, level + 1))
            except Exception as e:
                print(f"Error in future: {e}")

        time.sleep(random.uniform(0.1, 0.3))  # Small throttle

    return relationships

# Start crawling from Nike Inc
start_url = "https://www.importgenius.com/importers/nike-inc"
relationships = crawl_parallel(start_url, max_depth=7)

# Write to CSV with full URLs
with open("supplier.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["Parent", "Child"])
    writer.writeheader()
    for r in relationships:
        writer.writerow(r)

print("✅ Finished. Check 'supplier.csv'")
