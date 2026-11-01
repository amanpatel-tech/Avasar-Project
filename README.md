# Avasar 🎓

Avasar is an intelligent discovery platform that helps students in India find verified scholarships and hackathons before deadlines close. Powered by TinyFish web agents, Avasar searches live web sources and dispatches autonomous agents in parallel to extract critical details—including prize amounts, eligibility criteria, application deadlines, and direct apply links—surfacing actionable opportunities in an intuitive deadline-sorted interface.

**Live Application:** [https://avasar.streamlit.app](https://avasar.streamlit.app) *(Deploying to Streamlit Community Cloud)*

---

## Features

- **Live Web Agent Extraction:** Uses TinyFish AI web agents to read live web pages in parallel.
- **Accurate Metadata:** Extracts prize/grant amount, eligibility rules, closing date, and official links.
- **Urgency Chips & Sorting:** Automatically computes days remaining until the deadline and sorts opportunities.
- **Smart 30-Minute Cache:** Caches search results for 30 minutes with an instant "Search again" cache-bypass option.
- **CSV Export:** Download opportunity listings with one click.

---

## Local Setup & Run

### 1. Clone repository & install dependencies

```bash
git clone <YOUR_REPO_URL>
cd helperguidertinyfish
pip install -r requirements.txt
```

*(Recommended Python version: 3.12)*

### 2. Configure API Key

Create a `.env` file in the root folder with your TinyFish API key:

```env
TINYFISH_API_KEY=your_tinyfish_api_key_here
```

### 3. Launch App

```bash
streamlit run app.py
```

---

## Project Structure

- `app.py`: Streamlit frontend with Avasar branding, live agent progress indicators, and cached search.
- `finder.py`: Parallel TinyFish web search and multi-agent page scraping logic.
- `config.py`: Default search parameters and JSON extraction prompt/goal schema.
- `requirements.txt`: Minimal dependencies for deployment.
