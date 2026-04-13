from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

from bot.config import DEFAULT_MASTER_ENCRYPTION_KEY


class SecretBox:
    def __init__(self, encryption_key: str) -> None:
        self._raw_key = encryption_key.strip()
        self._fernet: Fernet | None = None
        if self.is_configured:
            self._fernet = Fernet(self._raw_key.encode("utf-8"))

    @property
    def is_configured(self) -> bool:
        return bool(self._raw_key) and self._raw_key != DEFAULT_MASTER_ENCRYPTION_KEY

    def encrypt(self, value: str) -> str:
        if not self._fernet:
            raise RuntimeError("MASTER_ENCRYPTION_KEY is not configured")
        return self._fernet.encrypt(value.encode("utf-8")).decode("utf-8")

    def decrypt(self, value: str) -> str:
        if not self._fernet:
            raise RuntimeError("MASTER_ENCRYPTION_KEY is not configured")
        try:
            return self._fernet.decrypt(value.encode("utf-8")).decode("utf-8")
        except InvalidToken as exc:
            raise RuntimeError("Stored secret cannot be decrypted") from exc
