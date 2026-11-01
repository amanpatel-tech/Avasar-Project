"""Stage 3: run all agents at the same time."""
import asyncio
import json

from tinyfish import AsyncTinyFish, RunStatus

from config import GOAL, OUTPUT_FILE, PAGES


async def main():
    client = AsyncTinyFish()
    runs = await asyncio.gather(*[
        client.agent.run(url=url, goal=GOAL)
        for url in PAGES.values()
    ])

    rows = []
    for company, run in zip(PAGES, runs):
        print(company, run.status)
        if run.status == RunStatus.COMPLETED:
            rows.append({"company": company, "roles": run.result})

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"Wrote {len(rows)} companies to {OUTPUT_FILE}")


asyncio.run(main())
# Too many at once? Extra runs wait in a queue, so they just take longer.
