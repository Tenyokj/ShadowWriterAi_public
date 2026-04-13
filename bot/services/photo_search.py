from __future__ import annotations

from dataclasses import dataclass

import httpx

from bot.config import DEFAULT_PIXABAY_API_KEY


@dataclass(slots=True)
class PhotoCandidate:
    url: str
    source_url: str
    author: str
    query: str
    provider: str


class PhotoSearchService:
    def __init__(
        self,
        pixabay_api_key: str,
        pixabay_api_url: str,
        pexels_api_key: str,
        pexels_api_url: str,
    ) -> None:
        self._pixabay_api_key = pixabay_api_key
        self._pixabay_api_url = pixabay_api_url
        self._pexels_api_key = pexels_api_key
        self._pexels_api_url = pexels_api_url
        self._client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        await self._client.aclose()

    async def search_photo(self, query: str, exclude_url: str | None = None) -> PhotoCandidate | None:
        candidates = await self.search_photos(query=query, limit=8)
        for candidate in candidates:
            if exclude_url and candidate.url == exclude_url:
                continue
            return candidate
        return None

    async def search_photos(self, query: str, limit: int = 5) -> list[PhotoCandidate]:
        if not query:
            return []

        candidates: list[PhotoCandidate] = []

        if self._pexels_api_key:
            candidates.extend(await self._search_pexels(query=query, limit=limit))

        if len(candidates) < limit and self._pixabay_api_key != DEFAULT_PIXABAY_API_KEY:
            pixabay_candidates = await self._search_pixabay(query=query, limit=limit)
            candidates.extend(pixabay_candidates)

        unique_by_url: dict[str, PhotoCandidate] = {}
        for candidate in candidates:
            unique_by_url.setdefault(candidate.url, candidate)

        return list(unique_by_url.values())[:limit]

    async def _search_pexels(self, query: str, limit: int) -> list[PhotoCandidate]:
        response = await self._client.get(
            self._pexels_api_url,
            headers={"Authorization": self._pexels_api_key},
            params={
                "query": query,
                "per_page": min(limit, 10),
                "orientation": "landscape",
            },
        )
        response.raise_for_status()
        data = response.json()
        photos = data.get("photos", [])
        results: list[PhotoCandidate] = []
        for item in photos:
            src = item.get("src", {})
            image_url = src.get("large2x") or src.get("large") or src.get("medium")
            if not image_url:
                continue
            results.append(
                PhotoCandidate(
                    url=image_url,
                    source_url=item.get("url", ""),
                    author=item.get("photographer", "Pexels"),
                    query=query,
                    provider="Pexels",
                )
            )
        return results

    async def _search_pixabay(self, query: str, limit: int) -> list[PhotoCandidate]:
        response = await self._client.get(
            self._pixabay_api_url,
            params={
                "key": self._pixabay_api_key,
                "q": query,
                "image_type": "photo",
                "safesearch": "true",
                "order": "popular",
                "per_page": min(limit, 10),
            },
        )
        response.raise_for_status()
        data = response.json()
        hits = data.get("hits", [])
        results: list[PhotoCandidate] = []
        for hit in hits:
            image_url = hit.get("largeImageURL") or hit.get("webformatURL")
            if not image_url:
                continue
            results.append(
                PhotoCandidate(
                    url=image_url,
                    source_url=hit.get("pageURL", ""),
                    author=hit.get("user", "Pixabay"),
                    query=query,
                    provider="Pixabay",
                )
            )
        return results
