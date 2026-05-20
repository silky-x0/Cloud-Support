import re
from typing import Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel

INJECTION_PATTERNS = [
    r"ignore (previous|all) instructions",
    r"act as (a|an|if)",
    r"disregard (your|the) (system|previous)",
    r"jailbreak",
    r"dan mode",
]

class GuardrailResult(BaseModel):
    passed: bool
    reason: Optional[str] = None

def check_input(text: str) -> GuardrailResult:
    # 1. Prompt Injection detection
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return GuardrailResult(passed=False, reason="prompt_injection")
            
    # 2. Length check (e.g., limit queries to 2048 characters to prevent denial-of-service / buffer issues)
    if len(text) > 2048:
        return GuardrailResult(passed=False, reason="length_exceeded")
        
    return GuardrailResult(passed=True)
