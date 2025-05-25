import logging
from .texts import texts

logger = logging.getLogger(__name__)

DEFAULT_LANG = "en"


def t(key: str, lang: str = "ua", **kwargs) -> str:
    """
    Get translated text by key and language.
    Falls back to default language if not found.
    """
    entry = texts.get(key)

    if not entry:
        logger.warning(f"Missing translation key: {key}")
        return key

    text = entry.get(lang) or entry.get(DEFAULT_LANG)

    if not text:
        logger.warning(f"Missing translation for key '{key}' in language '{lang}'")
        return key

    try:
        return text.format(**kwargs)
    except Exception as e:
        logger.error(f"Formatting error for key '{key}': {e}")
        return text
