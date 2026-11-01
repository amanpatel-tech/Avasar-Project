"""Stage 4: Search finds the pages, agents work them."""
import asyncio
import json

from tinyfish import AsyncTinyFish, RunStatus, TinyFish

from config import GOAL, MAX_SEARCH_PAGES, OUTPUT_FILE, SEARCH_QUERY

search_client = TinyFish()

# Search decides where to look (free up to 12,000 requests a day)
hits = search_client.search.query(query=SEARCH_QUERY)
urls = [r.url for r in hits.results[:MAX_SEARCH_PAGES]]
print("Search found:")
for u in urls:
    print(" ", u)


async def main():
    agents = AsyncTinyFish()
    runs = await asyncio.gather(*[
        agents.agent.run(url=u, goal=GOAL) for u in urls
    ])

    rows = []
    for u, run in zip(urls, runs):
        print(u, run.status)
        if run.status == RunStatus.COMPLETED:
            rows.append({"url": u, "roles": run.result})

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"Wrote {len(rows)} pages to {OUTPUT_FILE}")


asyncio.run(main())
