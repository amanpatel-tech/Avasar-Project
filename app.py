import html
import os
from datetime import date, datetime
from urllib.parse import urlparse

import pandas as pd
import streamlit as st
from dateutil import parser as dtparser
from dotenv import load_dotenv

from finder import run_finder

# Load local environment variables
load_dotenv()

# Read API key from os.environ first, then fallback to st.secrets
api_key = os.environ.get("TINYFISH_API_KEY")
if not api_key:
    try:
        if "TINYFISH_API_KEY" in st.secrets:
            api_key = st.secrets["TINYFISH_API_KEY"]
            os.environ["TINYFISH_API_KEY"] = api_key
    except Exception:
        pass

st.set_page_config(page_title="Avasar | Scholarships & Hackathons", page_icon="🎓", layout="wide")

st.markdown(
"""<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700;800&family=DM+Sans:wght@400;500;700&display=swap');
.stApp, .stApp p, .stApp label, .stApp input, .stApp button { font-family: 'DM Sans', sans-serif; }
.stApp { background: #F3F5F9; }
.block-container { max-width: 1080px; padding-top: 2rem; }
#MainMenu, footer, header { visibility: hidden; }
.brand-header { display: flex; align-items: center; gap: .75rem; margin-bottom: .6rem; }
.brand-title { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 2.1rem; color: #141B34; margin: 0; line-height: 1; letter-spacing: -0.5px; }
.brand-dot { color: #FFB020; }
.brand-badge { background: #FFF4E5; border: 1px solid #FFB020; color: #9A5A00; font-size: .75rem; font-weight: 700; padding: .2rem .6rem; border-radius: 999px; text-transform: uppercase; letter-spacing: .5px; }
.hero h1 { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 2.5rem; line-height: 1.15; color: #141B34; margin: .2rem 0 .5rem 0; padding: 0; max-width: 22ch; }
.hero p { color: #5B6482; font-size: 1.05rem; max-width: 62ch; margin: 0 0 1.3rem 0; }
[data-testid="stForm"] { background: #fff; border: 1px solid #DDE2EE; border-radius: 14px; padding: 1rem 1.2rem; }
.summary { color: #141B34; font-size: 1.05rem; font-weight: 500; padding-top: .3rem; }
.card { background: #fff; border: 1px solid #DDE2EE; border-radius: 14px; padding: 1.1rem 1.2rem 1.2rem 1.2rem; min-height: 260px; display: flex; flex-direction: column; gap: .6rem; margin-bottom: .4rem; border-top: 3px solid #2B3A8C; }
.card-top { display: flex; justify-content: space-between; align-items: center; gap: .6rem; }
.tag { font-size: .78rem; font-weight: 700; padding: .2rem .65rem; border-radius: 999px; }
.tag.schol { background: #D9F1EC; color: #0B5F57; }
.tag.hack { background: #E8E2FB; color: #4A2FC0; }
.chip { font-size: .8rem; font-weight: 700; padding: .2rem .6rem; border-radius: 6px; white-space: nowrap; }
.chip-urgent { background: #FDE3DC; color: #A32A0F; border: 1px solid #F5B5A6; }
.chip-soon { background: #FFF4E5; color: #8A5A00; border: 1px solid #FFD899; }
.chip-ok { background: #E3EEFF; color: #1F4BA8; border: 1px solid #B8D3FE; }
.chip-none { background: #EDEFF5; color: #5B6482; }
.chip-closed { background: #EDEFF5; color: #8A90A8; text-decoration: line-through; }
.card h3 { font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.2rem; line-height: 1.3; margin: 0; padding: 0; color: #141B34; }
.prize { font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.25rem; font-weight: 800; color: #2B3A8C; }
.meta { color: #5B6482; font-size: .93rem; line-height: 1.45; }
.meta b { color: #141B34; font-weight: 700; }
.actions { margin-top: auto; display: flex; align-items: center; gap: 1rem; padding-top: .3rem; }
a.apply { background: #2B3A8C; color: #fff !important; text-decoration: none; font-weight: 700; padding: .5rem 1.1rem; border-radius: 8px; display: inline-block; }
a.apply:hover { background: #1F2C6E; }
a.src { color: #5B6482 !important; font-size: .88rem; text-decoration: none; }
a.src:hover { text-decoration: underline; }
.empty { background: #fff; border: 1px dashed #C5CCE0; border-radius: 14px; padding: 1.6rem; color: #5B6482; }
.empty b { color: #141B34; }
</style>""",
    unsafe_allow_html=True,
)


def esc(value):
    return html.escape(str(value), quote=True)


def days_left(text):
    if not text:
        return None
    try:
        today = date.today()
        parsed = dtparser.parse(
            str(text), fuzzy=True, default=datetime(today.year, 12, 31)
        )
        return (parsed.date() - today).days
    except Exception:
        return None


def chip_for(days):
    if days is None:
        return "No date listed", "chip-none"
    if days < 0:
        return "Closed", "chip-closed"
    if days == 0:
        return "Closes today", "chip-urgent"
    label = f"{days} day left" if days == 1 else f"{days} days left"
    if days <= 7:
        return label, "chip-urgent"
    if days <= 30:
        return label, "chip-soon"
    return label, "chip-ok"


def safe_url(value):
    value = str(value or "")
    return value if value.startswith(("http://", "https://")) else ""


def card_html(item):
    is_hack = "hack" in str(item.get("type") or "").lower()
    tag_cls, tag_text = ("hack", "Hackathon") if is_hack else ("schol", "Scholarship")
    chip_text, chip_cls = chip_for(item["days"])

    name = esc(item.get("name") or "Untitled")
    prize = esc(item.get("amount_or_prize") or "Amount not listed")
    elig = esc(item.get("eligibility") or "Not listed on the page")
    deadline = esc(item.get("deadline") or "Not listed")

    apply_url = safe_url(item.get("apply_link")) or safe_url(item.get("source_url"))
    source_url = safe_url(item.get("source_url"))
    host = esc(urlparse(source_url).netloc.replace("www.", "")) if source_url else ""

    actions = ""
    if apply_url:
        actions += (
            f'<a class="apply" href="{esc(apply_url)}" target="_blank" '
            f'rel="noopener noreferrer">Apply</a>'
        )
    if source_url:
        actions += (
            f'<a class="src" href="{esc(source_url)}" target="_blank" '
            f'rel="noopener noreferrer">Found on {host}</a>'
        )

    return (
        '<div class="card">'
        f'<div class="card-top"><span class="tag {tag_cls}">{tag_text}</span>'
        f'<span class="chip {chip_cls}">{chip_text}</span></div>'
        f"<h3>{name}</h3>"
        f'<div class="prize">{prize}</div>'
        f'<div class="meta"><b>Deadline:</b> {deadline}</div>'
        f'<div class="meta"><b>Who can apply:</b> {elig}</div>'
        f'<div class="actions">{actions}</div>'
        "</div>"
    )


# ---------- Cache Function (30m TTL) ----------
@st.cache_data(ttl=1800, show_spinner=False)
def search_opportunities(query_text, _on_progress=None, _on_pages=None):
    return run_finder(query_text, on_progress=_on_progress, on_pages=_on_pages)


# ---------- Header & Branding ----------
st.markdown(
"""<div class="brand-header">
<svg width="34" height="34" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect width="36" height="36" rx="9" fill="#2B3A8C"/>
<path d="M18 7L28 12.5L18 18L8 12.5L18 7Z" fill="#FFB020"/>
<path d="M11 15.5V23C11 25.2 13.9 27.5 18 27.5C22.1 27.5 25 25.2 25 23V15.5L18 19.5L11 15.5Z" fill="#FFFFFF" fill-opacity="0.95"/>
<circle cx="28.5" cy="18.5" r="2.2" fill="#FFB020"/>
</svg>
<span class="brand-title">Avasar<span class="brand-dot">.</span></span>
<span class="brand-badge">India Student Edition</span>
</div>
<div class="hero">
<h1>Find scholarships and hackathons before they close</h1>
<p>Web agents open live pages, read them, and pull out the prize, eligibility and deadline for students in India.</p>
</div>""",
    unsafe_allow_html=True,
)

# Friendly API key check
if not api_key:
    st.warning(
        "⚠️ **TinyFish API Key is missing.** "
        "Please add `TINYFISH_API_KEY` to your `.env` file locally or in Streamlit Cloud Secrets."
    )

# ---------- Search form ----------
with st.form("search"):
    c1, c2, c3 = st.columns([2, 5, 2], vertical_alignment="bottom")
    kind = c1.selectbox("Looking for", ["Scholarship", "Hackathon"])
    topic = c2.text_input("Field or audience", "engineering students India")
    go = c3.form_submit_button(
        "Find opportunities", type="primary", use_container_width=True
    )
    search_again = st.checkbox(
        "Search again (bypass cache)",
        value=False,
        help="Bypass the 30-minute cache to fetch fresh live results from the web.",
    )

# ---------- Run search ----------
if go:
    if not api_key:
        st.error("Cannot perform search: TINYFISH_API_KEY is missing. Please configure your key first.")
    else:
        query = f"{kind.lower()}s for {topic} 2026 apply"
        if search_again:
            search_opportunities.clear()

        status_box = st.status("Searching the web...", expanded=True)

        def on_pages(urls):
            status_box.write(f"Found {len(urls)} pages. One agent is reading each page, all at once.")

        def on_progress(done, total, url, count, status):
            host = urlparse(url).netloc.replace("www.", "")
            if status == "ok":
                status_box.write(f"{host}: {count} listings found ({done} of {total} pages done)")
            else:
                status_box.write(f"{host}: could not read this page ({done} of {total} pages done)")

        try:
            rows = search_opportunities(query, _on_progress=on_progress, _on_pages=on_pages)
            status_box.update(label="Search finished", state="complete", expanded=False)
            st.session_state["rows"] = rows
        except Exception as err:
            status_box.update(label="Search failed", state="error", expanded=True)
            st.error(f"Something went wrong: {err}")
            st.session_state["rows"] = None

# ---------- Results ----------
rows = st.session_state.get("rows")

if rows is None:
    st.markdown(
"""<div class="empty"><b>Pick a type, name a field, and press Find opportunities.</b><br>
Try &ldquo;women in engineering&rdquo;, &ldquo;AI students India&rdquo; 
or &ldquo;first year B.Tech&rdquo;.</div>""",
        unsafe_allow_html=True,
    )
elif not rows:
    st.warning("No listings found. Try a broader field, like “students India”.")
else:
    seen, items = set(), []
    for row in rows:
        key = str(row.get("name") or "").strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        row["days"] = days_left(row.get("deadline"))
        items.append(row)

    s1, s2, s3 = st.columns([5, 2, 2], vertical_alignment="center")
    hide_closed = s3.toggle("Hide closed", value=True)
    sort_by = s2.selectbox("Sort by", ["Closing soonest", "Name"], label_visibility="collapsed")

    if hide_closed:
        items = [i for i in items if i["days"] is None or i["days"] >= 0]

    def order(i):
        d = i["days"]
        group = 1 if d is None else (2 if d < 0 else 0)
        return (group, d if d is not None else 0)

    if sort_by == "Closing soonest":
        items.sort(key=order)
    else:
        items.sort(key=lambda i: str(i.get("name")).lower())

    urgent = sum(1 for i in items if i["days"] is not None and 0 <= i["days"] <= 14)
    s1.markdown(
        f'<div class="summary">{len(items)} opportunities found. '
        f"{urgent} close within 14 days.</div>",
        unsafe_allow_html=True,
    )

    for start in range(0, len(items), 2):
        cols = st.columns(2)
        for col, item in zip(cols, items[start : start + 2]):
            col.markdown(card_html(item), unsafe_allow_html=True)

    export = pd.DataFrame(items).drop(columns=["days"], errors="ignore")
    st.download_button("Download CSV", export.to_csv(index=False), "opportunities.csv")
