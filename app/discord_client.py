
import logging

import requests

logger = logging.getLogger(__name__)


class DiscordClient:
    DISCORD_CONTENT_LIMIT = 2000

    def __init__(self, webhook_url: str, timeout: int = 20):
        self.webhook_url = webhook_url
        self.timeout = timeout
        self.session = requests.Session()

    def send(self, message: str) -> None:
        chunks = self._split_message(message)

        for index, chunk in enumerate(chunks, start=1):
            response = self.session.post(
                self.webhook_url,
                json={"content": chunk},
                timeout=self.timeout,
            )
            response.raise_for_status()
            logger.info(
                "Discord message %d/%d sent successfully",
                index,
                len(chunks),
            )

    @classmethod
    def _split_message(cls, message: str) -> list[str]:
        if len(message) <= cls.DISCORD_CONTENT_LIMIT:
            return [message]

        chunks = []
        current = ""

        for line in message.splitlines():
            candidate = f"{current}\n{line}".strip()

            if len(candidate) <= cls.DISCORD_CONTENT_LIMIT:
                current = candidate
                continue

            if current:
                chunks.append(current)

            # Handle a single unusually long line safely.
            while len(line) > cls.DISCORD_CONTENT_LIMIT:
                chunks.append(line[:cls.DISCORD_CONTENT_LIMIT])
                line = line[cls.DISCORD_CONTENT_LIMIT:]

            current = line

        if current:
            chunks.append(current)

        return chunks