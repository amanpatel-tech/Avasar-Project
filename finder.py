import asyncio
import json

from tinyfish import AsyncTinyFish, RunStatus, TinyFish

from config import GOAL, MAX_SEARCH_PAGES


def find_pages(query):
    """Search se pages dhoondho."""
    client = TinyFish()
    hits = client.search.query(query=query)
    results = getattr(hits, "results", []) or []
    return [r.url for r in results[:MAX_SEARCH_PAGES]]


def parse_items(result):
    """Result can be dict or text string. Handle both safely."""
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            return []
    if isinstance(result, dict):
        items = result.get("items", [])
        if isinstance(items, list):
            return [it for it in items if isinstance(it, dict)]
        return []
    return []


async def scrape_one(agents, url):
    """One agent per page. Never crashes, returns status."""
    try:
        run = await agents.agent.run(url=url, goal=GOAL)
    except Exception as e:
        return url, [], f"error: {e}"
    if run.status != RunStatus.COMPLETED:
        return url, [], "failed"
    items = parse_items(run.result)
    for item in items:
        if isinstance(item, dict):
            item["source_url"] = url
    return url, items, "ok"


async def scrape_all(urls, on_progress=None):
    """Run agents in parallel across all pages. Report as each finishes."""
    if not urls:
        return []
    agents = AsyncTinyFish()
    tasks = [asyncio.create_task(scrape_one(agents, u)) for u in urls]
    rows = []
    done = 0
    for finished in asyncio.as_completed(tasks):
        url, items, status = await finished
        done += 1
        rows.extend(items)
        if on_progress:
            on_progress(done, len(urls), url, len(items), status)
    return rows


def run_finder(query, on_progress=None, on_pages=None):
    urls = find_pages(query)
    if on_pages:
        on_pages(urls)
    if not urls:
        return []
    return asyncio.run(scrape_all(urls, on_progress))


if __name__ == "__main__":
    from config import SEARCH_QUERY

    data = run_finder(SEARCH_QUERY)
    print(json.dumps(data, indent=2, ensure_ascii=False))
