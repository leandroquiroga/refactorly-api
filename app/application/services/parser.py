from __future__ import annotations

class ResponseParser:
    """Splits an LLM response into annotated code and explanation.

    The LLM is prompted to separate sections with '### Detailed Explanation'.
    Everything before that marker is the annotated code, everything after is
    the explanation.
    """

    _MARKER = "### Detailed Explanation"
    
    def parse(self, raw: str) -> tuple[str, str]:
        """Split raw LLM output into (annotated_code, explanation)"""
        if self._MARKER in raw:
            annotated, explanation = raw.split(self._MARKER, 1)
            return annotated.strip(), explanation.strip()
        return raw.strip(), ""