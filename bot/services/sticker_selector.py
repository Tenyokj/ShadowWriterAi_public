class StickerSelector:
    def __init__(self, sticker_map: dict[str, str]) -> None:
        self._sticker_map = {key: value for key, value in sticker_map.items() if value}

    def pick(self, hint: str | None) -> str | None:
        if not hint:
            return None
        return self._sticker_map.get(hint)
