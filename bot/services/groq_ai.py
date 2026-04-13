from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

import httpx

from bot.database.db import ChannelProfile


@dataclass(slots=True)
class GeneratedPostDraft:
    text: str
    image_search_query: str | None = None
    sticker_hint: str | None = None


class GroqAIService:
    def __init__(
        self,
        api_key: str,
        model: str,
        api_url: str,
        models_api_url: str,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._api_url = api_url
        self._models_api_url = models_api_url
        self._client = httpx.AsyncClient(timeout=60.0)

    async def close(self) -> None:
        await self._client.aclose()

    async def generate_post_bundle(
        self,
        posts: list[str],
        idea: str,
        profile: ChannelProfile | None = None,
        language_code: str = "ru",
        facts_context: str | None = None,
        api_key_override: str | None = None,
        model_override: str | None = None,
        variation_instruction: str | None = None,
        previous_draft: str | None = None,
    ) -> GeneratedPostDraft:
        prompt = self._build_prompt(
            posts=posts,
            idea=idea,
            profile=profile,
            language_code=language_code,
            facts_context=facts_context,
            variation_instruction=variation_instruction,
            previous_draft=previous_draft,
        )
        payload = {
            "model": model_override or self._model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an elite Telegram channel editor. "
                        "Think through the style, pacing, hook, structure, emoji density, "
                        "and emotional tone internally. Write as if you are the real voice "
                        "of one specific channel with a stable identity, not a generic internet writer. "
                        "Return only valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.45 if facts_context else 0.7,
        }
        headers = self._headers(api_key_override)

        response = await self._client.post(
            self._api_url,
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        content = self._extract_text(data).strip()
        parsed = self._parse_json_payload(content)

        post_text = str(parsed.get("post_text", "")).strip()
        if not post_text:
            raise ValueError("Groq API вернул пустой post_text")

        if self._needs_revision(post_text, facts_mode=bool(facts_context)):
            post_text = await self._revise_post(
                original_post=post_text,
                posts=posts,
                idea=idea,
                profile=profile,
                language_code=language_code,
                facts_context=facts_context,
                api_key_override=api_key_override,
                model_override=model_override,
            )

        return GeneratedPostDraft(
            text=post_text,
            image_search_query=self._clean_optional_text(parsed.get("image_search_query")),
            sticker_hint=self._clean_optional_text(parsed.get("sticker_hint")),
        )

    async def generate_post(
        self,
        posts: list[str],
        idea: str,
        profile: ChannelProfile | None = None,
        language_code: str = "ru",
        facts_context: str | None = None,
        api_key_override: str | None = None,
        model_override: str | None = None,
    ) -> str:
        draft = await self.generate_post_bundle(
            posts=posts,
            idea=idea,
            profile=profile,
            language_code=language_code,
            facts_context=facts_context,
            api_key_override=api_key_override,
            model_override=model_override,
        )
        return draft.text

    async def validate_api_key(self, api_key: str) -> None:
        response = await self._client.get(
            self._models_api_url,
            headers=self._headers(api_key),
        )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("data"):
            raise ValueError("Groq returned no models for this key")

    @staticmethod
    def _build_prompt(
        posts: list[str],
        idea: str,
        profile: ChannelProfile | None = None,
        language_code: str = "ru",
        facts_context: str | None = None,
        variation_instruction: str | None = None,
        previous_draft: str | None = None,
    ) -> str:
        formatted_posts = "\n\n".join(f"{index}. {post}" for index, post in enumerate(posts, start=1))
        profile_block = GroqAIService._format_profile(profile)
        output_language = "English" if language_code == "en" else "Russian"
        factual_block = (
            f"\n\nФактический контекст и обязательные данные:\n{facts_context}\n"
            if facts_context
            else ""
        )
        factual_rules = (
            "- если выше даны фактические данные, опирайся только на них для цифр и формулировок про рынок\n"
            "- если выше даны фактические данные, обязательно включи минимум 5 конкретных числовых значений\n"
            "- если выше даны фактические данные, не подменяй цифры мотивационной водой или общими рассуждениями\n"
            "- если выше даны фактические данные, удобно подать их списком или компактными строками внутри поста\n"
            if facts_context
            else ""
        )
        variation_block = (
            f"\nДополнительная задача по вариативности:\n{variation_instruction}\n"
            if variation_instruction
            else ""
        )
        previous_draft_block = (
            f"\nПредыдущий вариант, от которого нужно заметно отличаться:\n{previous_draft}\n"
            if previous_draft
            else ""
        )
        return (
            "Проанализируй память о канале и примеры постов, а затем напиши сильный пост "
            "именно для этого канала.\n\n"
            f"{profile_block}\n\n"
            f"Вот примеры постов:\n{formatted_posts}\n\n"
            f"Теперь напиши новый пост на тему:\n{idea}\n\n"
            f"{factual_block}"
            f"{variation_block}"
            f"{previous_draft_block}"
            "Сделай внутренний анализ перед ответом, но не показывай его.\n"
            "Нужно вернуть JSON c полями:\n"
            f'- "post_text": готовый пост на языке {output_language}\n'
            '- "image_search_query": короткий поисковый запрос на английском для фотостока\n'
            '- "sticker_hint": одно из значений fire, idea, news, wow, none\n\n'
            "Требования к post_text:\n"
            "- не пиши как человек, который просто насёрфил фактов в интернете и пересказывает их\n"
            "- пиши как постоянный автор этого канала, который знает свою тему, аудиторию и голос\n"
            "- сохраняй ощущение единой редакционной линии канала\n"
            f"- итоговый текст должен быть написан полностью на языке {output_language}\n"
            "- повторяй стиль, ритм и лексику примеров\n"
            "- сделай текст содержательным, а не в 2 предложения\n"
            "- обычно это 5-10 фраз или 3-5 коротких абзацев, если тема не требует меньшего\n"
            "- не пиши сплошным полотном: разбивай текст на короткие абзацы\n"
            "- добавляй 2-5 уместных эмодзи по ходу текста, а не один случайный смайлик в самом конце\n"
            "- эмодзи должны усиливать смысл и ритм, а не выглядеть как украшение ради украшения\n"
            "- избегай шаблонных AI-фраз и канцелярита\n"
            "- если в профиле есть запреты, не нарушай их\n"
            "- если известен образ автора, держи именно этот голос\n"
            "- если дан предыдущий вариант, не копируй его структуру, хук и концовку почти дословно\n"
            "- если уместно, делай сильный хук в начале и ясную мысль в конце\n"
            "- текст должен звучать как живой авторский Telegram-пост, а не школьное сочинение или нейросетевой шаблон\n"
            f"{factual_rules}"
            "- верни только JSON без markdown и объяснений"
        )

    @staticmethod
    def _extract_text(data: dict[str, Any]) -> str:
        choices = data.get("choices", [])
        if not choices:
            raise ValueError("Groq API вернул пустой список choices")

        message = choices[0].get("message", {})
        content = message.get("content")
        if not content:
            raise ValueError("Groq API не вернул текст ответа")

        return str(content)

    @staticmethod
    def _clean_optional_text(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        if not text or text.lower() == "none":
            return None
        return text

    @staticmethod
    def _parse_json_payload(content: str) -> dict[str, Any]:
        for candidate in GroqAIService._json_candidates(content):
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                try:
                    # Tolerates raw newlines and other control characters inside strings.
                    return json.loads(candidate, strict=False)
                except json.JSONDecodeError:
                    continue

        extracted = GroqAIService._extract_fields_fallback(content)
        if extracted.get("post_text"):
            return extracted

        raise ValueError("Groq API вернул ответ не в JSON-формате")

    @staticmethod
    def _json_candidates(content: str) -> list[str]:
        candidates = [content]
        start_index = content.find("{")
        end_index = content.rfind("}")
        if start_index != -1 and end_index != -1 and end_index > start_index:
            candidates.append(content[start_index : end_index + 1])
        return candidates

    @staticmethod
    def _extract_fields_fallback(content: str) -> dict[str, Any]:
        normalized = content.replace("\r\n", "\n").replace("\r", "\n")

        def capture(key: str) -> str | None:
            patterns = [
                rf'"{key}"\s*:\s*"(?P<value>.*?)"\s*(?:,\s*"(?:post_text|image_search_query|sticker_hint)"\s*:|\}})\s*',
                rf"{key}\s*:\s*(?P<value>.+?)(?:\n(?:post_text|image_search_query|sticker_hint)\s*:|\Z)",
            ]
            for pattern in patterns:
                match = re.search(pattern, normalized, flags=re.DOTALL)
                if match:
                    value = match.group("value").strip()
                    value = value.replace('\\"', '"').replace("\\n", "\n")
                    return value.strip().strip('"')
            return None

        return {
            "post_text": capture("post_text"),
            "image_search_query": capture("image_search_query"),
            "sticker_hint": capture("sticker_hint"),
        }

    async def _revise_post(
        self,
        original_post: str,
        posts: list[str],
        idea: str,
        profile: ChannelProfile | None = None,
        language_code: str = "ru",
        facts_context: str | None = None,
        api_key_override: str | None = None,
        model_override: str | None = None,
    ) -> str:
        formatted_posts = "\n\n".join(
            f"{index}. {post}" for index, post in enumerate(posts, start=1)
        )
        profile_block = self._format_profile(profile)
        output_language = "English" if language_code == "en" else "Russian"
        factual_block = (
            f"\n\nФактические данные, которые нельзя искажать:\n{facts_context}\n"
            if facts_context
            else ""
        )
        factual_rules = (
            "- сохрани и явно покажи конкретные числа из factual data выше\n"
            "- не убирай цифры ради красоты текста\n"
            if facts_context
            else ""
        )
        payload = {
            "model": model_override or self._model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a senior Telegram editor. Rewrite weak drafts into posts that "
                        "feel human, rhythmic, expressive, native to Telegram, and deeply consistent "
                        "with the channel identity."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Улучши пост так, чтобы он звучал живее и сильнее.\n\n"
                        f"{profile_block}\n\n"
                        f"Тема:\n{idea}\n\n"
                        f"{factual_block}"
                        f"Примеры стиля канала:\n{formatted_posts}\n\n"
                        f"Черновик:\n{original_post}\n\n"
                        "Требования:\n"
                        f"- итоговый текст должен быть полностью на языке {output_language}\n"
                        "- сохрани основную мысль\n"
                        "- сделай так, чтобы чувствовался один и тот же автор, а не случайный копирайтер\n"
                        "- добавь ритм, нормальные абзацы и человеческую подачу\n"
                        "- добавь 2-5 уместных эмодзи по тексту\n"
                        "- не делай один эмодзи в самом конце как заглушку\n"
                        "- не делай текст слишком коротким\n"
                        f"{factual_rules}"
                        "- верни только готовый текст поста, без объяснений и без JSON"
                    ),
                },
            ],
            "temperature": 0.5 if facts_context else 0.8,
        }
        headers = self._headers(api_key_override)
        response = await self._client.post(
            self._api_url,
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        revised_text = self._extract_text(data).strip()
        return revised_text or original_post

    def _headers(self, api_key_override: str | None = None) -> dict[str, str]:
        api_key = api_key_override or self._api_key
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    @classmethod
    def _needs_revision(cls, post_text: str, facts_mode: bool = False) -> bool:
        text = post_text.strip()
        if len(text) < (180 if facts_mode else 220):
            return True
        if "\n" not in text:
            return True
        if not facts_mode and cls._count_emojis(text) < 2:
            return True
        if facts_mode and cls._count_numeric_tokens(text) < 5:
            return True
        return False

    @staticmethod
    def _count_emojis(text: str) -> int:
        total = 0
        for char in text:
            code = ord(char)
            if (
                0x1F300 <= code <= 0x1FAFF
                or 0x2600 <= code <= 0x26FF
                or 0x2700 <= code <= 0x27BF
            ):
                total += 1
        return total

    @staticmethod
    def _count_numeric_tokens(text: str) -> int:
        return len(re.findall(r"\d+(?:[.,]\d+)?", text))

    @staticmethod
    def _format_profile(profile: ChannelProfile | None) -> str:
        if profile is None:
            return (
                "Память о канале:\n"
                "- Данных пока мало\n"
                "- Опирайся на примеры постов и делай голос цельным"
            )

        profile_lines = [
            "Память о канале:",
            f"- Название: {profile.channel_title or 'неизвестно'}",
            f"- Описание: {profile.channel_description or 'неизвестно'}",
            f"- Главная тема: {profile.channel_topic or 'неизвестно'}",
            f"- Целевая аудитория: {profile.target_audience or 'неизвестно'}",
            f"- Образ автора/админа: {profile.admin_persona or 'неизвестно'}",
            f"- Типичные рубрики: {profile.content_pillars or 'неизвестно'}",
            f"- Стиль подачи: {profile.style_notes or 'неизвестно'}",
            f"- Стоп-темы: {profile.banned_topics or 'неизвестно'}",
        ]
        return "\n".join(profile_lines)
