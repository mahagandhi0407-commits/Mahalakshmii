from functools import lru_cache

from google import genai

from app.config import settings


@lru_cache(maxsize=1)
def get_gemini_client():
    if not settings.GOOGLE_API_KEY:
        return None

    return genai.Client(
        api_key=settings.GOOGLE_API_KEY,
    )


def gemini_available() -> bool:
    return bool(settings.GOOGLE_API_KEY)


def generate_structured(
    model: str,
    prompt: str,
    schema,
):
    client = get_gemini_client()

    if client is None:
        raise RuntimeError(
            "GOOGLE_API_KEY is not configured."
        )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": schema,
        },
    )

    if getattr(response, "parsed", None) is not None:
        return response.parsed

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return schema.model_validate_json(response.text)


def generate_text(
    model: str,
    prompt: str,
) -> str:
    client = get_gemini_client()

    if client is None:
        raise RuntimeError(
            "GOOGLE_API_KEY is not configured."
        )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    text = getattr(response, "text", None)

    if not text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return text.strip()