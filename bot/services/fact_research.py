from __future__ import annotations

from dataclasses import dataclass
from html import unescape
from urllib.parse import parse_qs, quote_plus, urljoin, urlparse
import re

import httpx


@dataclass(slots=True)
class ResearchSource:
    title: str
    url: str
    facts: list[str]


@dataclass(slots=True)
class ResearchSnapshot:
    context: str
    publication_block: str
    image_query: str | None = None
    sources: list[ResearchSource] | None = None


class FactResearchService:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            timeout=20.0,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
                )
            },
        )
        self._search_url = "https://html.duckduckgo.com/html/"

    async def close(self) -> None:
        await self._client.aclose()

    async def build_snapshot(self, idea: str, language_code: str) -> ResearchSnapshot:
        results = await self._search(idea)
        if not results:
            raise ValueError("No relevant web sources found")

        sources: list[ResearchSource] = []
        for title, url in results[:5]:
            facts = await self._extract_facts_from_page(url)
            if not facts:
                continue
            sources.append(ResearchSource(title=title, url=url, facts=facts[:2]))
            if len(sources) >= 3:
                break

        if not sources:
            raise ValueError("Could not extract reliable factual snippets from sources")

        return ResearchSnapshot(
            context=self._build_context(language_code, sources),
            publication_block=self._build_publication_block(language_code, sources),
            image_query=self._image_query_from_idea(idea),
            sources=sources,
        )

    async def _search(self, query: str) -> list[tuple[str, str]]:
        response = await self._client.get(
            self._search_url,
            params={"q": query},
        )
        response.raise_for_status()
        html = response.text

        matches = re.findall(
            r'<a[^>]*class="result__a"[^>]*href="(?P<href>[^"]+)"[^>]*>(?P<title>.*?)</a>',
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )

        results: list[tuple[str, str]] = []
        for href, raw_title in matches:
            title = self._strip_tags(unescape(raw_title))
            url = self._normalize_search_result_url(unescape(href))
            if not title or not url:
                continue
            if url.startswith("http"):
                results.append((title, url))
        return results

    async def _extract_facts_from_page(self, url: str) -> list[str]:
        response = await self._client.get(url, follow_redirects=True)
        response.raise_for_status()
        text = self._strip_html(response.text)
        sentences = self._split_sentences(text)
        fact_sentences: list[str] = []
        for sentence in sentences:
            if len(sentence) < 35 or len(sentence) > 320:
                continue
            if not re.search(r"\d", sentence):
                continue
            if not re.search(r"(?:\$|€|£|¥|usd|msrp|price|cost|starts at|starting at|from )", sentence.casefold()):
                continue
            fact_sentences.append(sentence)
            if len(fact_sentences) >= 3:
                break
        return fact_sentences

    @staticmethod
    def _normalize_search_result_url(url: str) -> str:
        if url.startswith("//"):
            return f"https:{url}"
        if url.startswith("/l/?"):
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            target = params.get("uddg", [None])[0]
            return unescape(target) if target else ""
        if url.startswith("/"):
            return urljoin("https://duckduckgo.com", url)
        return url

    @staticmethod
    def _strip_tags(text: str) -> str:
        return re.sub(r"<[^>]+>", "", text).strip()

    @classmethod
    def _strip_html(cls, html: str) -> str:
        html = re.sub(r"<script.*?>.*?</script>", " ", html, flags=re.IGNORECASE | re.DOTALL)
        html = re.sub(r"<style.*?>.*?</style>", " ", html, flags=re.IGNORECASE | re.DOTALL)
        text = cls._strip_tags(html)
        text = unescape(text)
        text = re.sub(r"\s+", " ", text)
        return text

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]

    def _build_context(self, language_code: str, sources: list[ResearchSource]) -> str:
        intro = (
            "Ниже подтверждённые факты из веб-источников. Используй только эти цифры и не выдумывай новые."
            if language_code == "ru"
            else "Below are verified facts from web sources. Use only these figures and do not invent new ones."
        )
        lines = [intro]
        for index, source in enumerate(sources, start=1):
            lines.append(f"Источник {index}: {source.title} — {source.url}" if language_code == "ru" else f"Source {index}: {source.title} — {source.url}")
            for fact in source.facts:
                lines.append(f"- {fact}")
        lines.append(
            "Если источники расходятся, честно покажи диапазон или оговори, что это разные оценки."
            if language_code == "ru"
            else "If the sources disagree, honestly present a range or note that the estimates differ."
        )
        return "\n".join(lines)

    def _build_publication_block(self, language_code: str, sources: list[ResearchSource]) -> str:
        header = "Подтверждённые факты:\n" if language_code == "ru" else "Verified facts:\n"
        lines: list[str] = []
        for source in sources:
            source_name = source.title[:60]
            for fact in source.facts[:1]:
                lines.append(
                    f"• {source_name}: {fact}"
                )
        return header + "\n".join(lines)

    @staticmethod
    def _image_query_from_idea(idea: str) -> str:
        cleaned = re.sub(r"[^\w\s-]", " ", idea, flags=re.UNICODE)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned[:80] or "news"
