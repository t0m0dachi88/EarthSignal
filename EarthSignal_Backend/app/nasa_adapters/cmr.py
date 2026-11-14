import httpx

CMR_BASE = "https://cmr.earthdata.nasa.gov/search"

class CMRService:
    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout

    async def collections(self, short_name: str | None = None, keyword: str | None = None, page_size: int = 10):
        params = {"page_size": min(max(page_size, 1), 50), "sort_key": "-revision_date"}
        if short_name:
            params["short_name"] = short_name
        if keyword:
            params["keyword"] = keyword
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{CMR_BASE}/collections.json", params=params)
            response.raise_for_status()
            payload = response.json()
        entries = payload.get("feed", {}).get("entry", [])
        return {
            "count": len(entries),
            "items": [
                {
                    "concept_id": e.get("id"),
                    "short_name": e.get("short_name"),
                    "version_id": e.get("version_id"),
                    "provider": e.get("provider_id"),
                    "title": e.get("entry_title"),
                    "summary": e.get("summary"),
                    "updated": e.get("revision_date"),
                    "links": e.get("links", [])[:5],
                }
                for e in entries
            ],
            "source": "NASA Common Metadata Repository (CMR)",
        }

    async def granules(self, collection_concept_id: str, temporal: str | None = None, page_size: int = 10):
        params = {"collection_concept_id": collection_concept_id, "page_size": min(max(page_size, 1), 50)}
        if temporal:
            params["temporal"] = temporal
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{CMR_BASE}/granules.json", params=params)
            response.raise_for_status()
            payload = response.json()
        entries = payload.get("feed", {}).get("entry", [])
        return {
            "count": len(entries),
            "items": [
                {
                    "concept_id": e.get("id"),
                    "title": e.get("title"),
                    "time_start": e.get("time_start"),
                    "time_end": e.get("time_end"),
                    "updated": e.get("updated"),
                    "producer_granule_id": e.get("producer_granule_id"),
                    "links": e.get("links", [])[:5],
                }
                for e in entries
            ],
            "source": "NASA Common Metadata Repository (CMR)",
        }
