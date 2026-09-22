"""Crawl English prompt pages from awesomevideoprompts.com into prompts.jsonl.

Polite by design: follows robots.txt (sitemap URLs only, no ?query URLs), 4 workers with a
small delay, retries with backoff, resumable (skips ids already saved). Text + metadata only.
Usage: python3 crawl_prompts.py [--limit N]
"""
import argparse
import html
import json
import re
import threading
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "prompts.jsonl"
UA = "Mozilla/5.0 (research; video-generation-cost-benchmark)"
SITEMAP = "https://awesomevideoprompts.com/sitemap.xml"
WORKERS, DELAY = 4, 0.25


def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(urllib.parse.quote(url, safe=":/?&=%"), headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 ** i)


def text(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def parse(url, page):
    slug = url.rsplit("/", 1)[1]
    paras = re.findall(r'<p class="copy-paragraph">(.*?)</p>', page, re.S)
    prompt = "\n".join(text(p) for p in paras)
    title = re.search(r'<h1 class="prompt-detail__title">(.*?)</h1>', page, re.S)
    date = re.search(r'<time class="meta-value">(.*?)</time>', page)
    models = re.findall(r'meta-link--model"[^>]*>(.*?)</a>', page, re.S)
    source = re.search(r'href="(https://x\.com/[^"]+)"[^>]*meta-link--source">(.*?)<', page)
    video = re.search(r'<video src="([^"]+)"', page)
    return {
        "id": slug.split("-", 1)[0],
        "slug": slug,
        "url": url,
        "title": text(title.group(1)) if title else "",
        "date": date.group(1) if date else "",
        "models": [text(m) for m in models],
        "source_url": source.group(1) if source else "",
        "source_author": text(source.group(2)) if source else "",
        "video_url": video.group(1) if video else "",
        "prompt": prompt,
        "words": len(prompt.split()),
        # Prompts that depend on uploaded images/videos cannot run on plain text-to-video.
        "needs_reference": bool(re.search(r"@image\d|@video\d|uploaded (?:reference )?(?:image|photo|video)|reference (?:image|video)", prompt, re.I)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    sitemap = get(SITEMAP)
    urls = [u for u in re.findall(r"<loc>([^<]+)</loc>", sitemap) if "/en/prompts/" in u and "?" not in u]
    done = set()
    if OUT.exists():
        done = {json.loads(l)["url"] for l in OUT.read_text().split("\n") if l.strip()}
    todo = [u for u in urls if u not in done][: args.limit]
    print(f"{len(urls)} prompt pages in sitemap, {len(done)} already saved, {len(todo)} to fetch", flush=True)

    lock, count, errors = threading.Lock(), [0], []
    fh = OUT.open("a")

    def work(url):
        try:
            rec = parse(url, get(url))
            with lock:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fh.flush()
                count[0] += 1
                if count[0] % 200 == 0:
                    print(f"{count[0]}/{len(todo)}", flush=True)
        except Exception as e:
            errors.append((url, repr(e)))
        time.sleep(DELAY)

    with ThreadPoolExecutor(WORKERS) as ex:
        list(ex.map(work, todo))
    print(f"done: {count[0]} saved, {len(errors)} errors", flush=True)
    for u, e in errors[:20]:
        print("ERR", u, e)


if __name__ == "__main__":
    main()
