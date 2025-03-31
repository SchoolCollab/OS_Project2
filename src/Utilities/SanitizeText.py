def SanitizeText(text: str) -> str:
    """Sanitize text by replacing invalid Unicode characters.

    ### Parameters
    - **text** `str`: The text to sanitize.

    ### Returns
    - **str**: The sanitized text.
    """
    return text.encode("utf-8", errors="replace").decode("utf-8")


__all__ = [
    "SanitizeText",
]
