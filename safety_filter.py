"""
Simple safety filter for AI replies. Detects self-harm phrases and censors the reply.
This is a minimal local heuristic filter. For production use, integrate a proper
safety classifier or policy service.
"""
from typing import Tuple, Optional
import logging
from datetime import datetime

SELF_HARM_KEYPHRASES = [
    "kill myself",
    "i want to die",
    "i'm going to kill myself",
    "end my life",
    "i want to end my life",
    "i am going to end my life",
    "suicide",
    "i want to commit suicide",
]

SAFE_RESPONSE = "I'm sorry, but I can't assist with that. If you're in immediate danger, please contact local emergency services or a crisis hotline."

# Additional safety categories with trigger phrases
SAFETY_CATEGORIES = {
    "self_harm": SELF_HARM_KEYPHRASES,
    "illegal_activity": [
        "how to make a bomb",
        "detonate",
        "how to make explosives",
        "make a weapon",
        "assassinate",
        "kill people",
        "harm others",
        "manufacture drugs",
        "how to make meth",
        "bypass security",
        "break into",
    ],
    "violence": [
        "kill",
        "murder",
        "beat someone",
        "stab",
    ],
    "sexual": [
        "sexual content",
        "porn",
        "explicit sexual",
    ],
}


CATEGORY_SAFE_MESSAGES = {
    "self_harm": SAFE_RESPONSE,
    "illegal_activity": "I can't help with instructions for illegal activities.",
    "violence": "I can't assist with violent or harmful actions.",
    "sexual": "I can't provide explicit sexual content.",
}


def check_and_filter(text: str) -> Tuple[bool, str, Optional[str]]:
    """Check text against safety categories.

    Returns (blocked, safe_text_or_original, category)
    If blocked is True, safe_text_or_original is the replacement message.
    """
    if not text:
        return False, text, None
    lower = text.lower()
    for category, phrases in SAFETY_CATEGORIES.items():
        for phrase in phrases:
            if phrase in lower:
                try:
                    logger = logging.getLogger('ai_safety')
                    if not logger.handlers:
                        handler = logging.FileHandler('ai_safety.log', encoding='utf-8')
                        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                        handler.setFormatter(formatter)
                        logger.addHandler(handler)
                        logger.setLevel(logging.INFO)
                    short = (text[:200] + '...') if len(text) > 200 else text
                    logger.info(f"Blocked reply category='{category}' trigger='{phrase}': {short}")
                except Exception:
                    pass
                safe = CATEGORY_SAFE_MESSAGES.get(category, SAFE_RESPONSE)
                return True, safe, category
    tokens = [t.strip(".,!?;:\"'()[]") for t in lower.split()]
    if 'kill' in tokens and ('yourself' in tokens or 'your self' in lower):
        try:
            logger = logging.getLogger('ai_safety')
            if not logger.handlers:
                handler = logging.FileHandler('ai_safety.log', encoding='utf-8')
                formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
            short = (text[:200] + '...') if len(text) > 200 else text
            logger.info(f"Blocked reply heuristic category='self_harm' trigger='kill+yourself': {short}")
        except Exception:
            pass
        return True, CATEGORY_SAFE_MESSAGES.get('self_harm', SAFE_RESPONSE), 'self_harm'
    if 'you' in tokens and ('should' in tokens or 'must' in tokens) and ('kill' in tokens or 'die' in tokens):
        try:
            logger = logging.getLogger('ai_safety')
            if not logger.handlers:
                handler = logging.FileHandler('ai_safety.log', encoding='utf-8')
                formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
            short = (text[:200] + '...') if len(text) > 200 else text
            logger.info(f"Blocked reply heuristic category='self_harm' trigger='you should kill/die': {short}")
        except Exception:
            pass
        return True, CATEGORY_SAFE_MESSAGES.get('self_harm', SAFE_RESPONSE), 'self_harm'
    return False, text, None


def filter_self_harm(text: str) -> Tuple[bool, str]:
    """Backward-compatible wrapper for the original function."""
    blocked, safe, cat = check_and_filter(text)
    return blocked, safe
