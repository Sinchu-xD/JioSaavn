import json


def extract_json(text: str) -> dict | None:
    start = text.find("{")
    if start == -1:
        return None

    candidate = text[start:]

    decoder = json.JSONDecoder()
    try:
        obj, _ = decoder.raw_decode(candidate)
        return obj
    except (json.JSONDecodeError, ValueError):
        return None
