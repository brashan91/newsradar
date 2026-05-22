"""
Léxico financiero v2 - Combinación de:
- Loughran-McDonald (palabras financieras académicas)
- Crypto-specific (HODL, FUD, ATH, moon, etc.)
- Patrones contextuales observados fallar en producción

Pesos:
  1 = señal débil (mención)
  2 = señal media (sentiment claro)
  3 = señal fuerte (decisivo, market-moving)
"""

# ============================================================================
# BULLISH (positive market signal)
# ============================================================================
BULLISH = {
    # Fuerza 3 - Movimientos brusco al alza
    "soar": 3, "soars": 3, "soaring": 3, "soared": 3,
    "surge": 3, "surges": 3, "surging": 3, "surged": 3,
    "rally": 3, "rallies": 3, "rallying": 3, "rallied": 3,
    "skyrocket": 3, "skyrockets": 3, "skyrocketed": 3,
    "rocketed": 3, "moonshot": 3,
    "explode": 3, "exploding": 3, "explosive gains": 3,
    "all-time high": 3, "all time high": 3, "record high": 3,
    "new high": 3, "new ath": 3, " ath ": 3, "new ath,": 3,
    "breakout": 3, "breaks out": 3, "broke out": 3,
    "to the moon": 3, "moon": 1,
    "buy signal": 3, "strong buy": 3,

    # Earnings positivos
    "beat estimates": 3, "beats estimates": 3, "beat expectations": 3,
    "beats expectations": 3, "beats analyst": 3, "beat analyst": 3,
    "surpassed estimates": 3, "surpassing estimates": 3,
    "exceeds expectations": 3, "exceeded expectations": 3,
    "raises guidance": 3, "raised guidance": 3, "lifts guidance": 3,
    "upgrade guidance": 3, "upgraded guidance": 3,
    "raises forecast": 3, "raised forecast": 3,
    "strong earnings": 3, "robust earnings": 3,
    "blowout earnings": 3, "blowout quarter": 3,
    "record revenue": 3, "record profit": 3, "record sales": 3,
    "stronger than expected": 3, "better than expected": 3,
    "delivered a solid": 3, "significantly beating": 3,
    "solid quarter": 2, "solid first quarter": 3,

    # Fuerza 2 - Subida clara / catalizadores positivos
    "rise": 2, "rises": 2, "rising": 2, "rose": 2, "risen": 2,
    "gain": 2, "gains": 2, "gaining": 2, "gained": 2,
    "climb": 2, "climbs": 2, "climbing": 2, "climbed": 2,
    "jump": 2, "jumps": 2, "jumping": 2, "jumped": 2,
    "leap": 2, "leaps": 2, "leaped": 2,
    "boost": 2, "boosts": 2, "boosted": 2, "boosting": 2,
    "bullish": 2, "bull market": 2, "bull run": 2,
    "buying activity": 2, "unusual buying": 2,
    "upgrade": 2, "upgraded": 2,
    "outperform": 2, "outperforms": 2, "outperformed": 2,
    "approved": 2, "approval": 2, "green light": 2, "greenlight": 2,
    "etf approved": 3, "etf approval": 3,
    "spot etf": 2,
    "partnership": 2, "deal signed": 2, "strategic partnership": 2,
    "acquires": 2, "acquisition": 2, "acquired": 2,
    "merger": 2,
    "expansion": 2, "expanding": 2, "expands": 2, "expand into": 2,
    "expands into": 2,
    "launches": 2, "launched": 2, "launching": 2,
    "introduces": 2, "introduce": 2, "introduced": 2,
    "unveiled": 2, "unveils": 2,
    "raises": 2, "raised": 2,
    "investment": 1, "invests": 2, "invested": 2,
    "bets heavily": 2, "betting heavily": 2,
    "going to": 1,
    "files for ipo": 3, "ipo filing": 3, "ipo announcement": 3,
    "confidentially files": 3, "files s-1": 2, "form s-1": 2,
    "listing": 2, "to be listed": 2, "going public": 2,
    "accumulating": 2, "accumulation": 2,
    "discovered": 2, "uncovers": 2, "uncovered": 2,
    "anomalies": 1,
    "new platform": 1, "new product": 1, "new service": 1,
    "new feature": 1,
    "tokenized": 1, "tokenized assets": 1,
    "milestone": 2, "achievement": 2,
    "breakthrough": 3, "breakthroughs": 3,
    "innovative": 1, "innovation": 1, "innovative solution": 2,
    "advancement": 2, "advances": 1,
    "infrastructure": 1,
    "stablecoin liquidity": 1, "deep liquidity": 2,
    "looking stronger": 2, "looking strong": 2,
    "stronger than": 2,
    "signs of life": 2, "loud one": 1,

    # Pre-IPO / valuations
    "valuation": 1, "trillion": 1, "billion": 0,
    "ttillion dollar": 2, "trillion-dollar": 2,
    "world's first": 2, "largest ever": 3, "largest in human history": 3,
    "trillionaire": 2, "first trillionaire": 3,

    # Whale activity
    "whale alert": 1,
    "whale withdrew": 1,
    "withdrew from": 1, "withdrawn from": 1,
    "removed from exchange": 2,
    "hodl": 1, "hodling": 1,

    # Fuerza 1 - Tendencia o mención positiva débil
    "up ": 1, "higher": 1, "advance": 1, "advances": 1, "advanced": 1,
    "positive": 1, "optimistic": 1, "strong": 1, "stronger": 1,
    "growth": 1, "growing": 1, "expand": 1,
    "buy ": 1, "buying": 1, "buyers": 1,
    "demand": 1, "high demand": 2, "strong demand": 2,
    "rebound": 1, "rebounds": 1, "rebounded": 1,
    "recovery": 1, "recovers": 1, "recovered": 1, "recovering": 1,
    "support": 1, "support level": 1,
    "potential": 1, "promising": 1,
    "robust": 1, "resilient": 1,
    "ai-assisted": 1, "ai-driven": 1, "ai solution": 1,
}


# ============================================================================
# BEARISH
# ============================================================================
BEARISH = {
    # Fuerza 3 - Caída brusca / colapso
    "crash": 3, "crashes": 3, "crashing": 3, "crashed": 3,
    "plunge": 3, "plunges": 3, "plunging": 3, "plunged": 3,
    "plummet": 3, "plummets": 3, "plummeted": 3,
    "tumble": 3, "tumbles": 3, "tumbled": 3,
    "collapse": 3, "collapses": 3, "collapsed": 3,
    "tank": 3, "tanks": 3, "tanked": 3,
    "wipeout": 3, "wiped out": 3, "wipe out": 3,
    "dump": 3, "dumps": 3, "dumped": 3,
    "selloff": 3, "sell-off": 3, "mass selling": 3, "panic selling": 3,
    "all-time low": 3, "record low": 3, "all time low": 3,
    "freefall": 3, "free fall": 3, "free-fall": 3,
    "capitulation": 3,

    # Earnings negativos
    "missed estimates": 3, "misses estimates": 3, "missed expectations": 3,
    "miss expectations": 3, "misses analyst": 3,
    "below estimates": 3, "fell short": 3, "fell short of estimates": 3,
    "cuts guidance": 3, "slashes guidance": 3, "lowered guidance": 3,
    "lowers guidance": 3, "guidance cut": 3,
    "warns of": 2, "profit warning": 3,
    "missing delivery": 3, "miss delivery": 3,
    "weak earnings": 3, "disappointing earnings": 3,
    "disappointing quarter": 3,
    "missing analyst expectations": 3,

    # Quiebras / problemas legales
    "bankruptcy": 3, "files for bankruptcy": 3, "chapter 11": 3,
    "insolvent": 3, "insolvency": 3,
    "fraud charges": 3, "indicted": 3, "indictment": 3,
    "sec lawsuit": 3, "doj investigation": 3, "criminal probe": 3,
    "money laundering": 3,
    "ponzi": 3, "ponzi scheme": 3,
    "rugpull": 3, "rug pull": 3, "rugged": 3,
    "exploit": 2, "hack": 3, "hacked": 3, "stolen": 3, "drained": 3,
    "drained from": 3, "lost millions": 3, "lost billions": 3,
    "losing millions": 3, "bleeding": 3,
    "exploits": 2, "exploited": 2,

    "strong sell": 3, "sell signal": 3,

    # Fuerza 2 - Caída clara
    "fall": 2, "falls": 2, "falling": 2, "fell": 2, "fallen": 2,
    "drop": 2, "drops": 2, "dropping": 2, "dropped": 2,
    "decline": 2, "declines": 2, "declining": 2, "declined": 2,
    "slide": 2, "slides": 2, "sliding": 2, "slid": 2,
    "slump": 2, "slumps": 2, "slumped": 2,
    "loss": 2, "losses": 2, "losing": 2,
    "bearish": 2, "bear market": 2,
    "downgrade": 2, "downgrades": 2, "downgraded": 2,
    "underperform": 2, "underperforms": 2, "underperformed": 2,
    "rejected": 2, "denied": 2, "blocked": 2,
    "layoffs": 2, "layoff": 2, "fired": 2, "job cuts": 2,
    "delisted": 2, "delisting": 2,
    "selling activity": 2, "unusual selling": 2,
    "withdrawn from binance": 1,
    "withdrew from #binance": 1,

    # Patrones técnicos bajistas
    "turned lower": 2, "turning lower": 2, "turns lower": 2,
    "lower from": 2,
    "pulls back": 2, "pulled back": 2, "pullback": 2,
    "weakening": 2, "weakening demand": 3,
    "weak economy": 3, "weak demand": 2,
    "cooling demand": 3, "cooling off": 2, "cooled": 2, "cooling": 2,
    "outflows": 3, "outflow": 2, "etf outflows": 3,
    "spot bitcoin etf outflows": 3,
    "resistance": 1, "rejected at": 2, "rejection": 2, "technical rejection": 3,
    "fails breakout": 3, "failed breakout": 3, "fails to break": 3, "failed to break": 3,
    "fails to sustain": 3, "failed to sustain": 3,
    "fails to": 2,
    "below its": 1, "trading below": 2, "below the": 1,
    "below resistance": 2, "below support": 2,

    # Macro bearish
    "warns": 2, "warning": 2, "warned": 2,
    "calls interest rates": 1,
    "far too restrictive": 3, "too restrictive": 3,
    "restrictive monetary": 2,
    "monetary policy is too tight": 3,
    "supply shocks": 2, "supply shock": 2,
    "deficient demand": 3,
    "prolonged period": 2,
    "alarm": 2, "sounding an alarm": 3,
    "tensions": 2, "iran tensions": 3, "geopolitical tensions": 3,
    "redirects": 2, "redirected": 2,
    "vessels redirected": 3,
    "military strike": 3, "missile attack": 3, "warfare": 3,
    "decrease in": 1, "reduction in": 1,

    # Cyber/exploit context
    "hack losses": 3, "crypto hack": 3,
    "north korea-linked": 2, "north korea linked": 2,
    "criminal actors": 2,
    "automated reconnaissance": 1,
    "targeted": 1,
    "unverified smart contracts": 2,

    # Fuerza 1 - Tendencia negativa débil
    "down ": 1, "lower": 1, "weak": 1, "weaker": 1,
    "negative": 1, "pessimistic": 1, "concerns": 1, "worry": 1, "worries": 1,
    "sell": 1, "selling": 1, "distribute": 1,
    "uncertainty": 1, "uncertain": 1,
    "pressure": 2, "headwinds": 2,
    "cool": 1, "cooler": 1,
    "fail": 1, "fails": 1, "failed": 1, "failing": 1,
    "scrutiny": 2, "regulatory scrutiny": 2,
    "criticized": 1, "criticism": 1, "criticised": 1,
    "fud": 2, "fear uncertainty": 2,
    "rekt": 3,
    "dead": 2, "dying": 2,
}


# ============================================================================
# PAUSE / UNCERTAINTY
# ============================================================================
PAUSE = {
    # Fuerza 3 - Eventos macro críticos
    "fomc meeting": 3, "fed meeting": 3, "rate decision": 3,
    "powell speech": 3, "jerome powell": 3,
    "cpi report": 3, "inflation report": 3, "jobs report": 3,
    "nonfarm payrolls": 3, "nfp ": 3, "nfp report": 3,
    "earnings season": 3, "earnings call": 3,
    "war ": 3, "warfare": 3,
    "central bank": 3, "bank of england": 2, "ecb decision": 3,
    "interest rates": 2,
    "rate cut": 2, "rate hike": 2,
    "monetary policy committee": 2, "mpc": 2, "mpc member": 2,
    "fed chair": 3,

    # Fuerza 2 - Regulación / política
    "regulation": 2, "regulatory": 2, "regulators": 2,
    "regulatory scrutiny": 2,
    "sec ruling": 2, "sec decision": 2, "sec investigation": 3,
    "sec files lawsuit": 3, "sec lawsuit": 3, "sec filed": 3,
    "files lawsuit": 3, "filed lawsuit": 3,
    "lawsuit filed": 3, "investigation": 2,
    "unregistered securities": 3,
    "alleging": 2,
    "ban": 2, "banned": 2, "banning": 2,
    "tariffs": 2, "tariff": 2, "trade war": 3,
    "geopolitical": 2, "sanctions": 2, "sanctioned": 2,
    "election": 2, "elections": 2,

    # Fuerza 1 - Incertidumbre general
    "volatility": 1, "volatile": 1, "choppy": 1, "sideways": 1,
    "consolidation": 1, "consolidating": 1,
    "wait and see": 1, "cautious": 1, "caution": 1, "cautiously": 1,
    "fed ": 1, "federal reserve": 2, "ecb": 1, "boj ": 1,
    "boe ": 2, "bank of england": 2,
    "inflation": 1, "deflation": 1, "recession": 2, "stagflation": 2,
    "uncertain market conditions": 2,
    "market snapshot": 0,
    "subject to market conditions": 1,
}


# ============================================================================
# SOURCE IMPACT por dominio
# ============================================================================
SOURCE_IMPACT = {
    "bloomberg.com": "high", "reuters.com": "high", "wsj.com": "high",
    "ft.com": "high", "cnbc.com": "high", "marketwatch.com": "high",
    "sec.gov": "high", "federalreserve.gov": "high",
    "bls.gov": "high", "bea.gov": "high", "treasury.gov": "high",
    "ecb.europa.eu": "high", "bankofengland.co.uk": "high",

    "coindesk.com": "high", "cointelegraph.com": "high",
    "decrypt.co": "high", "theblock.co": "high",
    "bitcoinmagazine.com": "high",

    "yahoo.com": "medium", "finance.yahoo.com": "medium",
    "seekingalpha.com": "medium", "benzinga.com": "medium",
    "investopedia.com": "medium",
    "cryptopanic.com": "medium", "cryptoslate.com": "medium",
    "cryptobriefing.com": "medium",

    "t.me": "low", "telegram": "low", "reddit.com": "low",
    "twitter.com": "low", "x.com": "low", "nitter": "low",
}


def get_impact_for_url(url: str) -> str:
    url_lower = (url or "").lower()
    for domain, impact in SOURCE_IMPACT.items():
        if domain in url_lower:
            return impact
    return "medium"
