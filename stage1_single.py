"""Stage 1: send one agent to one careers page."""
from tinyfish import RunStatus, TinyFish

from config import GOAL, PAGES

client = TinyFish()  # reads TINYFISH_API_KEY

company, url = next(iter(PAGES.items()))
print(f"Sending an agent to {company} ({url}). This takes 30 to 90 seconds...")

run = client.agent.run(url=url, goal=GOAL)

# COMPLETED only means the agent finished. Always read the result.
print("status:", run.status)
if run.status == RunStatus.COMPLETED:
    print(run.result)
    if not run.result:
        print("Empty result. Try a clearer goal, or another page.")
