from dataclasses import dataclass


@dataclass
class ParsedPage:
    page_number: int | None
    text: str


@dataclass
class ParsedVisual:
    asset_index: int
    page_number: int | None

    asset_type: str

    storage_path: str
    mime_type: str | None

    checksum_sha256: str | None

    width_px: int | None
    height_px: int | None


@dataclass
class ParseResult:
    pages: list[ParsedPage]

    visuals: list[ParsedVisual]

    page_count: int | None  