"""Stage 2: loop over many pages, one at a time, and save the results."""
import json

from tinyfish import RunStatus, TinyFish

from config import GOAL, OUTPUT_FILE, PAGES

client = TinyFish()

rows = []
for company, url in PAGES.items():
    print(f"Working on {company}...")
    run = client.agent.run(url=url, goal=GOAL)
    print(f"  status: {run.status}")
    if run.status == RunStatus.COMPLETED:
        rows.append({"company": company, "roles": run.result})

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2)

print(f"Wrote {len(rows)} companies to {OUTPUT_FILE}")
# This loop runs one page at a time. Stage 3 runs them all at once.
