import re
from typing import Optional

INJECTION_PATTERNS = [
    r"ignore (all|previous) instructions",
    r"disregard (all|previous) instructions",
    r"system prompt",
    r"developer message",
    r"reveal .*prompt",
    r"you are chatgpt",
    r"bypass",
]

def detect_prompt_injection(text: str) -> Optional[str]:
    t = text.lower()
    for pat in INJECTION_PATTERNS:
        if re.search(pat, t):
            return pat
    return None