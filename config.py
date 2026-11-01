import os
from dotenv import load_dotenv

load_dotenv()

SEARCH_QUERY = "scholarships for Indian engineering students 2026 apply"
MAX_SEARCH_PAGES = 5
OUTPUT_FILE = "results.json"

GOAL = """
Find scholarships or hackathons listed on this page.
Return ONLY valid JSON in this exact format:
{
  "items": [
    {
      "name": "string",
      "type": "scholarship or hackathon",
      "amount_or_prize": "string or null",
      "deadline": "string or null",
      "eligibility": "string or null",
      "apply_link": "string or null"
    }
  ]
}
Rules:
- Extract at most 10 items.
- If a field is not on the page, use null. Never guess.
- If the page has no scholarships or hackathons, return {"items": []}.
- If a CAPTCHA or login wall appears, stop and return {"items": []}.
"""