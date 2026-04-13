from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re

import httpx


@dataclass(slots=True)
class CryptoPricePoint:
    coin_id: str
    symbol: str
    display_name_ru: str
    display_name_en: str
    price_usd: float
    change_24h: float | None

    def display_name(self, language_code: str) -> str:
        return self.display_name_en if language_code == "en" else self.display_name_ru


@dataclass(slots=True)
class CryptoMarketSnapshot:
    context: str
    publication_block: str
    image_query: str
    sources: list[dict[str, object]]


class CryptoPriceService:
    _COINS: dict[str, dict[str, str]] = {
        "bitcoin": {
            "symbol": "BTC",
            "ru": "Биткоин",
            "en": "Bitcoin",
        },
        "ethereum": {
            "symbol": "ETH",
            "ru": "Эфириум",
            "en": "Ethereum",
        },
        "solana": {
            "symbol": "SOL",
            "ru": "Солана",
            "en": "Solana",
        },
        "ripple": {
            "symbol": "XRP",
            "ru": "XRP",
            "en": "XRP",
        },
        "binancecoin": {
            "symbol": "BNB",
            "ru": "BNB",
            "en": "BNB",
        },
        "dogecoin": {
            "symbol": "DOGE",
            "ru": "Dogecoin",
            "en": "Dogecoin",
        },
        "toncoin": {
            "symbol": "TON",
            "ru": "Toncoin",
            "en": "Toncoin",
        },
        "cardano": {
            "symbol": "ADA",
            "ru": "Cardano",
            "en": "Cardano",
        },
        "tron": {
            "symbol": "TRX",
            "ru": "TRON",
            "en": "TRON",
        },
        "avalanche-2": {
            "symbol": "AVAX",
            "ru": "Avalanche",
            "en": "Avalanche",
        },
    }
    _ALIASES: dict[str, str] = {
        "bitcoin": "bitcoin",
        "btc": "bitcoin",
        "биткоин": "bitcoin",
        "биток": "bitcoin",
        "ethereum": "ethereum",
        "eth": "ethereum",
        "эфир": "ethereum",
        "эфириум": "ethereum",
        "solana": "solana",
        "sol": "solana",
        "солана": "solana",
        "ripple": "ripple",
        "xrp": "ripple",
        "binance": "binancecoin",
        "bnb": "binancecoin",
        "doge": "dogecoin",
        "dogecoin": "dogecoin",
        "додж": "dogecoin",
        "ton": "toncoin",
        "toncoin": "toncoin",
        "тон": "toncoin",
        "cardano": "cardano",
        "ada": "cardano",
        "tron": "tron",
        "trx": "tron",
        "avax": "avalanche-2",
        "avalanche": "avalanche-2",
    }
    _DEFAULT_IDS = [
        "bitcoin",
        "ethereum",
        "solana",
        "ripple",
        "binancecoin",
        "dogecoin",
    ]

    def __init__(self, api_url: str) -> None:
        self._api_url = api_url
        self._client = httpx.AsyncClient(timeout=20.0)

    async def close(self) -> None:
        await self._client.aclose()

    def requires_live_prices(self, idea: str) -> bool:
        normalized = self._normalize(idea)
        crypto_markers = (
            "крипт",
            "crypto",
            "coin",
            "btc",
            "eth",
            "sol",
            "xrp",
            "bnb",
            "doge",
            "ton",
            "ada",
            "trx",
            "avax",
            "биткоин",
            "эфир",
            "эфириум",
            "солана",
        )
        price_markers = (
            "цен",
            "price",
            "prices",
            "quote",
            "quotes",
            "курс",
            "котиров",
            "сколько стоит",
        )
        exact_markers = (
            "цифр",
            "digits",
            "exact",
            "точн",
            "numbers",
            "числ",
        )
        has_crypto = any(marker in normalized for marker in crypto_markers)
        has_price_intent = any(marker in normalized for marker in price_markers)
        wants_exact = any(marker in normalized for marker in exact_markers)
        return has_crypto and (has_price_intent or wants_exact)

    async def build_snapshot(self, idea: str, language_code: str) -> CryptoMarketSnapshot:
        coin_ids = self._extract_coin_ids(idea)
        points = await self.fetch_prices(coin_ids=coin_ids)
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        intro = (
            "Ниже live-данные рынка из CoinGecko. Используй именно эти цифры как factual basis."
            if language_code == "ru"
            else "Below is live market data from CoinGecko. Use these figures as the factual basis."
        )
        time_line = (
            f"Снимок данных: {generated_at}"
            if language_code == "ru"
            else f"Data snapshot: {generated_at}"
        )

        lines = [intro, time_line]
        for point in points:
            price_text = self._format_price(point.price_usd)
            change_text = self._format_change(point.change_24h)
            lines.append(
                f"- {point.display_name(language_code)} ({point.symbol}): ${price_text} | 24h: {change_text}"
            )

        lines.append(
            "Обязательное правило: не заменяй эти цифры общими рассуждениями, включи в текст минимум 5 конкретных значений."
            if language_code == "ru"
            else "Mandatory rule: do not replace these figures with vague commentary; include at least 5 concrete values in the post."
        )
        return CryptoMarketSnapshot(
            context="\n".join(lines),
            publication_block=self._build_publication_block(points, generated_at, language_code),
            image_query="crypto market chart",
            sources=self._build_sources(points, generated_at, language_code),
        )

    async def fetch_prices(self, coin_ids: list[str]) -> list[CryptoPricePoint]:
        response = await self._client.get(
            self._api_url,
            params={
                "ids": ",".join(coin_ids),
                "vs_currencies": "usd",
                "include_24hr_change": "true",
            },
        )
        response.raise_for_status()
        payload = response.json()
        points: list[CryptoPricePoint] = []
        for coin_id in coin_ids:
            item = payload.get(coin_id)
            if not item or "usd" not in item:
                continue
            coin_meta = self._COINS[coin_id]
            points.append(
                CryptoPricePoint(
                    coin_id=coin_id,
                    symbol=coin_meta["symbol"],
                    display_name_ru=coin_meta["ru"],
                    display_name_en=coin_meta["en"],
                    price_usd=float(item["usd"]),
                    change_24h=float(item["usd_24h_change"]) if item.get("usd_24h_change") is not None else None,
                )
            )
        if not points:
            raise ValueError("CoinGecko returned no price data")
        return points

    def _extract_coin_ids(self, idea: str) -> list[str]:
        normalized = self._normalize(idea)
        matches: list[str] = []
        for alias, coin_id in self._ALIASES.items():
            if re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", normalized):
                if coin_id not in matches:
                    matches.append(coin_id)
        return matches[:6] or self._DEFAULT_IDS

    @staticmethod
    def _normalize(text: str) -> str:
        return text.casefold().replace("ё", "е")

    @staticmethod
    def _format_price(value: float) -> str:
        if value >= 1000:
            return f"{value:,.2f}"
        if value >= 1:
            return f"{value:,.3f}"
        return f"{value:,.6f}"

    @staticmethod
    def _format_change(value: float | None) -> str:
        if value is None:
            return "n/a"
        prefix = "+" if value >= 0 else ""
        return f"{prefix}{value:.2f}%"

    def _build_publication_block(
        self,
        points: list[CryptoPricePoint],
        generated_at: str,
        language_code: str,
    ) -> str:
        header = (
            f"Срез рынка на {generated_at}:\n"
            if language_code == "ru"
            else f"Market snapshot as of {generated_at}:\n"
        )
        lines = []
        for point in points:
            lines.append(
                f"• {point.symbol} — ${self._format_price(point.price_usd)} ({self._format_change(point.change_24h)} за 24ч)"
                if language_code == "ru"
                else f"• {point.symbol} — ${self._format_price(point.price_usd)} ({self._format_change(point.change_24h)} in 24h)"
            )
        return header + "\n".join(lines)

    def _build_sources(
        self,
        points: list[CryptoPricePoint],
        generated_at: str,
        language_code: str,
    ) -> list[dict[str, object]]:
        facts = []
        for point in points:
            facts.append(
                f"{point.display_name(language_code)} ({point.symbol}) — ${self._format_price(point.price_usd)} | 24h: {self._format_change(point.change_24h)}"
            )
        title = (
            f"CoinGecko live market snapshot ({generated_at})"
            if language_code == "en"
            else f"CoinGecko live-снимок рынка ({generated_at})"
        )
        return [
            {
                "title": title,
                "url": "https://www.coingecko.com/",
                "facts": facts[:6],
            }
        ]
