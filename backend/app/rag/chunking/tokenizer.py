import tiktoken


class TokenCounter:

    def __init__(
        self,
        encoding_name: str = "cl100k_base",
    ):

        self.encoding_name = (
            encoding_name
        )

        self.encoding = (
            tiktoken.get_encoding(
                encoding_name
            )
        )

    def encode(
        self,
        text: str,
    ) -> list[int]:

        return self.encoding.encode(
            text,
            disallowed_special=(),
        )

    def decode(
        self,
        tokens: list[int],
    ) -> str:

        return self.encoding.decode(
            tokens
        )

    def count(
        self,
        text: str,
    ) -> int:

        return len(
            self.encode(text)
        )

    def head(
        self,
        text: str,
        max_tokens: int,
    ) -> str:

        tokens = self.encode(text)

        return self.decode(
            tokens[:max_tokens]
        )

    def tail(
        self,
        text: str,
        max_tokens: int,
    ) -> str:

        tokens = self.encode(text)

        return self.decode(
            tokens[-max_tokens:]
        )