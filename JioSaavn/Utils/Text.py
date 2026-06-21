_HTML_ENTITIES: dict[str, str] = {
    "&quot;": '"',
    "&apos;": "'",
    "&#039;": "'",
    "&amp;": "&",
    "&lt;": "<",
    "&gt;": ">",
    "&nbsp;": " ",
}


def clean(text: str | None) -> str:
    if not text:
        return ""
    for entity, char in _HTML_ENTITIES.items():
        text = text.replace(entity, char)
    return text.strip()
