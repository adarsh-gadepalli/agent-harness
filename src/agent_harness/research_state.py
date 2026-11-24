class Sources:
    """Assigns each URL a stable numeric id so the model can cite [n] instead of copying URLs."""

    def __init__(self):
        self.by_url: dict[str, int] = {}
        self.items: dict[int, dict] = {}

    def add(self, url: str, title: str = "") -> int:
        """Register a URL and return its id. Re-adding a known URL returns the same id."""
        if url in self.by_url:
            source_id = self.by_url[url]
            if title and not self.items[source_id]["title"]:
                self.items[source_id]["title"] = title
            return source_id
        source_id = len(self.items) + 1
        self.by_url[url] = source_id
        self.items[source_id] = {"url": url, "title": title}
        return source_id

    def get(self, source_id: int) -> dict | None:
        return self.items.get(source_id)

    def clear(self) -> None:
        self.by_url.clear()
        self.items.clear()


SOURCES = Sources()
