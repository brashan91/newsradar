"""
NewsRadar Analyzer v2 - HYBRID approach.

Pipeline:
1. VADER (sentiment universal, vendored en analyzer/vendor/vader/)
2. Custom financial lexicon (bullish/bearish/pause con pesos)
3. Reglas contextuales (negaciones, patrones IPO/earnings/lawsuit)
4. Detección agresiva de tickers ($TSLA, NYSE:, nombres)
5. Fusión y decisión final

Output compatible con schema ns_article_analysis de Supabase.
"""

import os
import re
import sys
from typing import Optional

# Importar VADER desde vendor local (NO pip)
_VADER_DIR = os.path.join(os.path.dirname(__file__), "vendor", "vader")
sys.path.insert(0, _VADER_DIR)
from vaderSentiment import SentimentIntensityAnalyzer  # noqa: E402

from .tickers import (
    detect_tickers_aggressive, categorize,
    CRYPTO_SET, CRYPTO_ECOSYSTEM, INDICES,
)
from .lexicon import BULLISH, BEARISH, PAUSE, get_impact_for_url


# ============================================================================
# Compilación de regex (una sola vez al arranque)
# ============================================================================
def _build_regex(word_dict):
    escaped = [re.escape(w) for w in word_dict.keys()]
    escaped.sort(key=len, reverse=True)
    pattern = r'\b(' + '|'.join(escaped) + r')\b'
    return re.compile(pattern, re.IGNORECASE)


_BULLISH_RE = _build_regex(BULLISH)
_BEARISH_RE = _build_regex(BEARISH)
_PAUSE_RE = _build_regex(PAUSE)

NEGATORS = {
    "fail", "fails", "failed", "failing",
    "not", "no", "never", "n't",
    "doesn't", "doesnt", "does not",
    "didn't", "didnt", "did not",
    "won't", "wont", "will not",
    "couldn't", "couldnt", "could not",
    "without", "lacks", "lacking",
}
_NEGATOR_RE = re.compile(
    r'\b(' + '|'.join(re.escape(n) for n in NEGATORS) + r')\b',
    re.IGNORECASE,
)

# VADER analyzer global
_VADER = SentimentIntensityAnalyzer()


# ============================================================================
# Reglas contextuales
# ============================================================================
CONTEXTUAL_RULES = [
    # IPO / Going Public -> BULLISH
    (re.compile(r'\b(?:confidentially\s+)?files?\s+for\s+(?:u\.?s\.?\s+)?ipo\b', re.I), "bullish", 4),
    (re.compile(r'\b(?:files?|submits?)\s+(?:draft\s+)?(?:form\s+)?s-1\b', re.I), "bullish", 3),
    (re.compile(r'\b(?:initial\s+public\s+offering|going\s+public)\b', re.I), "bullish", 3),
    (re.compile(r'\bipo\s+(?:announcement|filing)\b', re.I), "bullish", 4),
    (re.compile(r'\bwave\s+of\s+(?:crypto\s+)?listings?\b', re.I), "bullish", 3),

    # Earnings beat / miss
    (re.compile(r'\bbeat(?:s|ing)?\s+(?:analyst\s+)?(?:expectations|estimates|forecasts)\b', re.I), "bullish", 4),
    (re.compile(r'\bsurpass(?:ed|ing)?\s+(?:analyst\s+)?(?:expectations|estimates)\b', re.I), "bullish", 4),
    (re.compile(r'\bmiss(?:ed|ing|es)?\s+(?:analyst\s+)?(?:expectations|estimates|delivery)\b', re.I), "bearish", 4),
    (re.compile(r'\bfell\s+short\s+of\s+(?:estimates|expectations)\b', re.I), "bearish", 4),
    (re.compile(r'\bsignificantly\s+beat(?:ing)?\b', re.I), "bullish", 4),
    (re.compile(r'\bdelivered\s+a\s+solid\s+(?:first\s+|second\s+|third\s+|fourth\s+)?quarter\b', re.I), "bullish", 3),

    # New product / partnership / expansion -> BULLISH
    (re.compile(r'\b(?:expand|expands|expanding|expansion)\s+(?:into|to)\b', re.I), "bullish", 2),
    (re.compile(r'\bnew\s+platform\s+for\b', re.I), "bullish", 2),
    (re.compile(r'\bintroduces?\s+(?:new\s+)?(?:hybrid|advanced|innovative)\b', re.I), "bullish", 2),
    (re.compile(r'\bunveil(?:s|ed)?\s+(?:new|latest)\b', re.I), "bullish", 2),
    (re.compile(r'\b(?:strategic\s+)?partnership\s+with\b', re.I), "bullish", 2),

    # AI/Tech catalysts -> BULLISH bias
    (re.compile(r'\b(?:agentic\s+)?ai\s+solution\b', re.I), "bullish", 2),
    (re.compile(r'\bai-(?:powered|driven|assisted|enabled)\b', re.I), "bullish", 2),
    (re.compile(r'\bbets?\s+(?:heavily|big)\s+on\s+ai\b', re.I), "bullish", 3),
    (re.compile(r'\blargest\s+(?:actionable\s+)?(?:total\s+)?addressable\s+market\b', re.I), "bullish", 4),
    (re.compile(r'\btrillionaire\b', re.I), "bullish", 3),
    (re.compile(r'\b(?:trillion-dollar|2t)\s+valuation\b', re.I), "bullish", 3),

    # Discovery / new resources -> BULLISH commodities
    (re.compile(r'\buncovers?\s+\d+\s+(?:copper|gold|silver|lithium|nickel|iron)\s+(?:anomalies|deposits|reserves)\b', re.I), "bullish", 3),
    (re.compile(r'\bdiscovered?\s+\d+\s+(?:anomalies|deposits)\b', re.I), "bullish", 3),
    (re.compile(r'\bai-assisted\s+(?:exploration\s+)?(?:study|analysis)\b', re.I), "bullish", 2),

    # Whale activity
    (re.compile(r'\bunusual\s+buying\s+activity\b', re.I), "bullish", 3),
    (re.compile(r'\bunusual\s+selling\s+activity\b', re.I), "bearish", 3),
    (re.compile(r'\bwhale\s+(?:withdrew|transferred|moved)\b', re.I), "bullish", 1),
    (re.compile(r'\bwhale\s+deposited\b', re.I), "bearish", 2),

    # Earnings positivos (TJX-style)
    (re.compile(r'\bsigns?\s+of\s+life\s+in\s+retail\b', re.I), "bullish", 3),
    (re.compile(r'\b(?:stock|shares)\s+(?:is\s+)?looking\s+stronger\b', re.I), "bullish", 3),
    (re.compile(r'\bstrong(?:er)?\s+than\s+(?:it\s+has\s+been\s+)?in\s+years\b', re.I), "bullish", 3),
    (re.compile(r'\bsignificantly\s+beating\s+(?:analyst\s+)?expectations\b', re.I), "bullish", 4),

    # Geopolítica / War -> bearish para risk-on
    (re.compile(r'\b(?:us\s+)?redirects?\s+\d+\s+vessels?\b', re.I), "bearish", 3),
    (re.compile(r'\b(?:iran|china|russia|israel)\s+tensions?\b', re.I), "pause", 3),
    (re.compile(r'\bstrait\s+of\s+hormuz\b', re.I), "pause", 2),
    (re.compile(r'\bmilitary\s+(?:strike|attack|action)\b', re.I), "bearish", 3),
    (re.compile(r'\bcentcom\b', re.I), "pause", 2),

    # Lawsuit / regulation
    (re.compile(r'\bsec\s+files?\s+(?:a\s+)?lawsuit\s+against\b', re.I), "pause", 4),
    (re.compile(r'\bfor\s+unregistered\s+securities\b', re.I), "pause", 3),
    (re.compile(r'\b(?:doj|fbi|cftc)\s+investigation\b', re.I), "pause", 3),
    (re.compile(r'\bregulatory\s+scrutiny\b', re.I), "pause", 2),

    # Bank/Macro warnings
    (re.compile(r'\b(?:bank\s+of\s+england|boe|bce|ecb|fed)\s+(?:official|member|chair|governor)\b', re.I), "pause", 2),
    (re.compile(r'\bfed\s+(?:warns?|signals?)\b', re.I), "pause", 3),
    (re.compile(r'\b(?:rates|interest\s+rates)\s+(?:may|will|could)\s+stay\s+higher\s+for\s+longer\b', re.I), "pause", 4),
    (re.compile(r'\bwarns?\s+(?:that\s+)?(?:the\s+)?(?:uk|us|eu|global)\s+economy\s+is\s+weak\b', re.I), "bearish", 4),
    (re.compile(r'\binterest\s+rates?\s+(?:are\s+)?(?:far\s+)?too\s+restrictive\b', re.I), "bearish", 4),
    (re.compile(r'\bcalls?\s+for\s+rate\s+cuts?\b', re.I), "bearish", 2),
    (re.compile(r'\bsupply\s+shocks?\s+(?:are\s+)?stoking\s+inflation\b', re.I), "bearish", 3),
    (re.compile(r'\bweak\s+economy\b', re.I), "bearish", 3),

    # DeFi / Hacks / Exploits
    (re.compile(r'\b(?:lost|losing|drained)\s+(?:over\s+)?\$\d+(?:\.\d+)?\s*(?:billion|million|m|b)\b', re.I), "bearish", 4),
    (re.compile(r'\bdefi\s+(?:protocols?\s+)?(?:keeps?\s+)?losing\b', re.I), "bearish", 4),
    (re.compile(r'\b(?:hack|exploit|drain|rugpull)(?:ed|ing)?\b', re.I), "bearish", 3),
    (re.compile(r'\bnorth\s+korea[\s-]linked\b', re.I), "bearish", 2),

    # New ATH (siempre bullish strong)
    (re.compile(r'\b(?:new\s+)?ath\b', re.I), "bullish", 3),
    (re.compile(r'\b(?:made|hit|reached)\s+(?:a\s+)?new\s+(?:all[- ]?time\s+)?high\b', re.I), "bullish", 4),
    (re.compile(r'\bcrossing\s+over\s+\$\d', re.I), "bullish", 3),

    # Withdrawals (matiz)
    (re.compile(r'\bnewly\s+created\s+wallet\s+withdrew\b', re.I), "bullish", 2),

    # Spanish (telegram)
    (re.compile(r'\bse\s+llevan\s+(?:los\s+)?vip\s+un\s+\+\d', re.I), "bullish", 2),
    (re.compile(r'\bapunta\s+que\s+(?:se\s+)?(?:va\s+a\s+|sube\s+a\s+|llega\s+a\s+)', re.I), "bullish", 2),
]


# ============================================================================
# Negaciones
# ============================================================================
def has_negator_before(text: str, match_start: int, window: int = 25) -> bool:
    start = max(0, match_start - window)
    chunk = text[start:match_start].lower()
    return bool(_NEGATOR_RE.search(chunk))


# ============================================================================
# Scoring
# ============================================================================
def score_lexicon(text: str) -> dict:
    if not text:
        return {"bullish": 0, "bearish": 0, "pause": 0, "matches": []}

    bull_score = 0
    bear_score = 0
    matches = []

    for m in _BULLISH_RE.finditer(text):
        w = m.group(1).lower()
        weight = BULLISH.get(w, 1)
        if has_negator_before(text, m.start()):
            bear_score += max(1, weight // 2 + 1)
            matches.append(f"~bull({w})={weight}")
        else:
            bull_score += weight
            matches.append(f"bull({w})={weight}")

    for m in _BEARISH_RE.finditer(text):
        w = m.group(1).lower()
        weight = BEARISH.get(w, 1)
        if has_negator_before(text, m.start()):
            bull_score += max(1, weight // 2)
            matches.append(f"~bear({w})={weight}")
        else:
            bear_score += weight
            matches.append(f"bear({w})={weight}")

    pause_score = 0
    for m in _PAUSE_RE.finditer(text):
        w = m.group(1).lower()
        weight = PAUSE.get(w, 1)
        pause_score += weight
        matches.append(f"pause({w})={weight}")

    return {
        "bullish": bull_score,
        "bearish": bear_score,
        "pause": pause_score,
        "matches": matches,
    }


def score_contextual_rules(text: str) -> dict:
    bull, bear, pause = 0, 0, 0
    matches = []
    for pattern, polarity, weight in CONTEXTUAL_RULES:
        if pattern.search(text):
            if polarity == "bullish":
                bull += weight
            elif polarity == "bearish":
                bear += weight
            elif polarity == "pause":
                pause += weight
            matches.append(f"rule:{polarity}+{weight}")
    return {"bullish": bull, "bearish": bear, "pause": pause, "matches": matches}


def score_vader(text: str) -> dict:
    if not text:
        return {"bullish": 0, "bearish": 0, "compound": 0}
    scores = _VADER.polarity_scores(text)
    compound = scores["compound"]
    if compound > 0.05:
        return {"bullish": int(compound * 5), "bearish": 0, "compound": compound}
    elif compound < -0.05:
        return {"bullish": 0, "bearish": int(abs(compound) * 5), "compound": compound}
    return {"bullish": 0, "bearish": 0, "compound": compound}


# ============================================================================
# Decisión final
# ============================================================================
def decide(scores: dict, tickers: list) -> tuple:
    bull = scores["bullish"]
    bear = scores["bearish"]
    pause = scores["pause"]
    total = bull + bear + pause

    if total < 2:
        return ("neutral", "neutral", 0.1)

    if pause >= bull + bear and pause >= 3:
        confidence = min(pause / 12.0, 0.85)
        if bear > bull * 1.5:
            return ("pause", "bearish", round(confidence, 2))
        return ("pause", "neutral", round(confidence, 2))

    margin = abs(bull - bear)

    if margin < 2:
        confidence = min(max(bull, bear) / 12.0, 0.4)
        return ("neutral", "neutral", round(confidence, 2))

    if bull > bear:
        confidence = min(bull / 12.0, 0.95)
        sentiment = "bullish"
        if bull >= 4 and confidence >= 0.35:
            return ("buy", sentiment, round(confidence, 2))
        return ("neutral", sentiment, round(confidence, 2))

    confidence = min(bear / 12.0, 0.95)
    sentiment = "bearish"
    if bear >= 4 and confidence >= 0.35:
        return ("sell", sentiment, round(confidence, 2))
    return ("neutral", sentiment, round(confidence, 2))


# ============================================================================
# Función principal
# ============================================================================
def analyze(headline: str, body: Optional[str] = None,
            url: Optional[str] = None) -> dict:
    """
    Analiza un artículo y devuelve dict compatible con ns_article_analysis.

    Returns:
      {
        "signal": "buy|sell|pause|neutral",
        "sentiment": "bullish|bearish|neutral",
        "confidence": float 0-1,
        "tickers": [str],
        "market_impact": "low|medium|high",
        "categories": [str],
        "time_horizon": "intraday|days|weeks|months",
        "_debug": {...}
      }
    """
    headline = (headline or "").strip()
    body = (body or "")[:800]

    boosted = f"{headline}. {headline}. {body}"
    full_text = f"{headline}. {body}"

    # 1. Tickers
    tickers = detect_tickers_aggressive(full_text)

    # 2. Scoring multi-fuente
    lex_scores = score_lexicon(boosted)
    rule_scores = score_contextual_rules(full_text)
    vader_scores = score_vader(full_text)

    # 3. Fusión: reglas peso 2x, lexicon 1x, VADER 0.5x
    combined = {
        "bullish": lex_scores["bullish"] + rule_scores["bullish"] * 2 + int(vader_scores["bullish"] * 0.5),
        "bearish": lex_scores["bearish"] + rule_scores["bearish"] * 2 + int(vader_scores["bearish"] * 0.5),
        "pause":   lex_scores["pause"] + rule_scores["pause"] * 2,
    }

    # 4. Decisión
    signal, sentiment, confidence = decide(combined, tickers)

    # 5. Impact
    source_impact = get_impact_for_url(url) if url else "medium"
    total_score = combined["bullish"] + combined["bearish"] + combined["pause"]

    if source_impact == "high" and total_score >= 5:
        impact = "high"
    elif source_impact == "low" and total_score < 5:
        impact = "low"
    elif total_score >= 10:
        impact = "high"
    elif total_score >= 4:
        impact = "medium"
    else:
        impact = source_impact

    # 6. Categorías
    categories = categorize(tickers)
    if combined["pause"] >= 4 and "macro" not in categories:
        categories.append("macro")
    if not tickers and combined["pause"] >= 3 and "macro" not in categories:
        categories.append("macro")

    # 7. Time horizon
    text_lower = full_text.lower()
    if any(w in text_lower for w in ["today", "intraday", "this morning", "this afternoon", "minutes ago", "now ", "right now"]):
        time_horizon = "intraday"
    elif any(w in text_lower for w in ["this week", "next week", "tomorrow", " days "]):
        time_horizon = "days"
    elif any(w in text_lower for w in ["this month", "next month", "quarter", "weeks"]):
        time_horizon = "weeks"
    elif any(w in text_lower for w in ["long term", "this year", "annual", "year-end", "yearly", "fiscal"]):
        time_horizon = "months"
    else:
        time_horizon = "days"

    return {
        "signal": signal,
        "sentiment": sentiment,
        "confidence": confidence,
        "tickers": tickers,
        "market_impact": impact,
        "categories": categories,
        "time_horizon": time_horizon,
        "_debug": {
            "combined": combined,
            "lexicon": lex_scores,
            "rules": rule_scores,
            "vader": vader_scores,
            "source_impact": source_impact,
        }
    }
