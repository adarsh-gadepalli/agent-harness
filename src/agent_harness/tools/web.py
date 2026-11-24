import time
import warnings

warnings.filterwarnings("ignore", message="SOCKS support in urllib3")

import httpx  # noqa: E402
import trafilatura  # noqa: E402
from ddgs import DDGS  # noqa: E402

from agent_harness.research_state import SOURCES
from agent_harness.tools.registry import tool

PAGE_CHARS = 6000  # ~1500 tokens per page of text
SEARCH_DELAY_SECONDS = 1.0
FETCH_TIMEOUT_SECONDS = 15
USER_AGENT = "Mozilla/5.0 (compatible; agent-harness/0.1; research bot)"

_page_cache: dict[str, list[str]] = {}
_last_search_at = 0.0


@tool(risk="network")
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web. Returns numbered results with title, URL, and a short snippet.
    Each result starts with a source id like [3]. Use fetch_page on a result's URL to read the full page."""
    global _last_search_at
    wait = SEARCH_DELAY_SECONDS - (time.monotonic() - _last_search_at)
    if wait > 0:
        time.sleep(wait)
    _last_search_at = time.monotonic()

    results = DDGS().text(query, max_results=max_results)
    if not results:
        return "No results."

    lines = []
    for r in results:
        source_id = SOURCES.add(r["href"], r.get("title", ""))
        lines.append(f"[{source_id}] {r.get('title', '')}\n    {r['href']}\n    {r.get('body', '')}")
    return "\n".join(lines)


@tool(risk="network")
def fetch_page(url: str, page: int = 1) -> str:
    """Read the main text of a web page. Long pages are split into pages of ~1500 tokens;
    the header says 'page X of N'. Call again with page=2, 3, ... to keep reading."""
    if url not in _page_cache:
        response = httpx.get(
            url,
            timeout=FETCH_TIMEOUT_SECONDS,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )
        response.raise_for_status()
        text = trafilatura.extract(response.text)
        if not text:
            return f"Error: no readable text found at {url} (it may need JavaScript or a login). Try another source."
        _page_cache[url] = [text[i : i + PAGE_CHARS] for i in range(0, len(text), PAGE_CHARS)]

    pages = _page_cache[url]
    if not 1 <= page <= len(pages):
        return f"Error: page {page} is out of range; this document has {len(pages)} page(s)."

    source_id = SOURCES.add(url)
    return f"[{source_id}] {url} (page {page} of {len(pages)})\n\n{pages[page - 1]}"
