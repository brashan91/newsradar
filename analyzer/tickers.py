"""
Diccionario de tickers v2 con detección agresiva.

Mejoras vs v1:
- Soporte para símbolos $TICKER y #TICKER (Telegram/social)
- Patrones "NYSE: TICKER", "NASDAQ: TICKER", "(TSLA)"
- Stablecoins y altcoins extendidas (BFUSD, FDUSD, ALLO, HYPE...)
- Companies-as-tickers via product names (iPhone -> AAPL, etc.)
- Aliases bidireccionales
"""

import re

# Tickers reconocidos: ticker -> [aliases en headline/body]
TICKERS = {
    # ============ MAJOR CRYPTO (bot Binance v2 + top market cap) ============
    "BTC":   ["bitcoin", "btc", "btc/usd", "btcusd", "btcusdt", "$btc", "#btc"],
    "ETH":   ["ethereum", "eth", "ether", "ethusd", "ethusdt", "$eth", "#eth"],
    "SOL":   ["solana", "$sol", "#sol", "solusdt"],
    "BNB":   ["binance coin", "bnb", "$bnb", "bnbusdt"],
    "XRP":   ["ripple", "xrp", "$xrp", "xrpusdt"],
    "ADA":   ["cardano", "$ada", "adausdt"],
    "AVAX":  ["avalanche", "avax", "$avax", "avaxusdt"],
    "DOGE":  ["dogecoin", "doge", "$doge", "dogeusdt"],
    "LINK":  ["chainlink", "$link", "linkusdt"],
    "POL":   ["polygon", "matic", "$matic", "$pol", "polusdt", "maticusdt"],
    "DOT":   ["polkadot", "$dot", "dotusdt"],
    "ATOM":  ["cosmos", "$atom", "atomusdt"],
    "NEAR":  ["near protocol", "$near", "nearusdt"],
    "LTC":   ["litecoin", "ltc", "$ltc", "ltcusdt"],
    "BCH":   ["bitcoin cash", "bch", "$bch", "bchusdt"],

    # Stablecoins
    "USDT":  ["tether", "usdt"],
    "USDC":  ["usd coin", "usdc"],
    "DAI":   ["dai stablecoin", "$dai"],
    "FDUSD": ["fdusd", "$fdusd", "#fdusd", "first digital usd"],
    "BFUSD": ["bfusd", "$bfusd", "#bfusd", "binance futures usd"],
    "BUSD":  ["busd"],

    # Altcoins relevantes (top 100)
    "TRX":   ["tron", "$trx"],
    "TON":   ["toncoin", "ton coin", "$ton"],
    "SHIB":  ["shiba inu", "$shib"],
    "PEPE":  ["pepe coin", "$pepe"],
    "WIF":   ["dogwifhat", "$wif"],
    "BONK":  ["bonk coin", "$bonk"],
    "ARB":   ["arbitrum", "$arb"],
    "OP":    ["optimism token", "$op"],
    "SUI":   ["sui network", "$sui"],
    "APT":   ["aptos", "$apt"],
    "ICP":   ["internet computer", "$icp"],
    "FIL":   ["filecoin", "$fil"],
    "AAVE":  ["aave protocol", "$aave"],
    "UNI":   ["uniswap", "$uni"],
    "MKR":   ["makerdao", "maker dao", "$mkr"],
    "HYPE":  ["hyperliquid", "$hype", "#hype"],
    "ZEC":   ["zcash", "$zec", "#zec"],
    "ALLO":  ["allora network", "$allo", "#allo"],

    # ============ CRYPTO ECOSYSTEM (companies) ============
    "COIN":  ["coinbase", "blockchain.com"],
    "MSTR":  ["microstrategy", "strategy inc", "saylor"],
    "HOOD":  ["robinhood"],
    "RIOT":  ["riot platforms", "riot blockchain"],
    "MARA":  ["marathon digital"],
    "CLSK":  ["cleanspark"],
    "GLXY":  ["galaxy digital"],
    "MPAY":  ["moonpay"],

    # ============ PRE-IPO / PRIVATE (relevantes mercado) ============
    "OPENAI": ["openai", "open ai"],
    "ANTHRO": ["anthropic"],
    "SPACEX": ["spacex", "space-x", "starlink"],
    "STRIPE": ["stripe inc"],
    "CANVA":  ["canva inc"],
    "DISCRD": ["discord inc"],

    # ============ MEGA CAP TECH ============
    "NVDA":  ["nvidia", "$nvda"],
    "AAPL":  ["apple inc", "iphone", "tim cook", "$aapl"],
    "MSFT":  ["microsoft", "$msft"],
    "GOOGL": ["google", "alphabet", "sundar pichai", "$googl", "$goog"],
    "AMZN":  ["amazon", "$amzn", "bezos"],
    "META":  ["meta platforms", "facebook", "instagram", "whatsapp", "zuckerberg", "$meta"],
    "TSLA":  ["tesla", "elon musk", "cybertruck", "$tsla", "spacex"],
    "NFLX":  ["netflix", "$nflx"],
    "AMD":   ["amd ", "advanced micro devices", "$amd"],
    "INTC":  ["intel ", "$intc"],
    "ORCL":  ["oracle", "$orcl"],
    "CRM":   ["salesforce", "$crm"],
    "ADBE":  ["adobe systems", "$adbe"],
    "AVGO":  ["broadcom", "$avgo"],
    "TSM":   ["tsmc", "taiwan semiconductor"],
    "ASML":  ["asml holding"],

    # ============ STOCKS DIVIDEND WATCHLIST ============
    "O":     ["realty income"],
    "MAIN":  ["main street capital"],
    "VICI":  ["vici properties"],
    "EPR":   ["epr properties"],
    "VZ":    ["verizon"],
    "T":     ["at&t"],
    "ENB":   ["enbridge"],
    "RIO":   ["rio tinto"],
    "MO":    ["altria"],
    "BTI":   ["british american tobacco"],
    "PM":    ["philip morris"],
    "AMT":   ["american tower"],
    "ESS":   ["essex property"],
    "MAA":   ["mid-america apartment"],
    "SPG":   ["simon property group"],
    "BXMT":  ["blackstone mortgage"],
    "KREF":  ["kkr real estate"],
    "LTCN":  ["ltc properties"],
    "IIPR":  ["innovative industrial properties"],
    "WPC":   ["w. p. carey", "w.p. carey"],
    "WEC":   ["wec energy"],
    "VOD":   ["vodafone"],

    # ============ BANKS & FINANCE ============
    "JPM":   ["jpmorgan", "jp morgan", "$jpm"],
    "BAC":   ["bank of america", "$bac"],
    "GS":    ["goldman sachs", "$gs"],
    "MS":    ["morgan stanley", "$ms"],
    "WFC":   ["wells fargo", "$wfc"],
    "C":     ["citigroup", "$c"],
    "BRK":   ["berkshire hathaway", "warren buffett"],
    "BLK":   ["blackrock", "$blk"],
    "V":     ["visa inc"],
    "MA":    ["mastercard inc"],

    # ============ ENERGY / COMMODITIES ============
    "XOM":   ["exxonmobil", "exxon mobil", "$xom"],
    "CVX":   ["chevron", "$cvx"],
    "SHEL":  ["shell oil", "royal dutch shell"],

    # ============ RETAIL ============
    "TJX":   ["tjx companies", "tj maxx", "marshalls", "homegoods", "$tjx"],
    "WMT":   ["walmart", "$wmt"],
    "TGT":   ["target corp", "$tgt"],
    "COST":  ["costco wholesale", "$cost"],

    # ============ OTROS RELEVANTES ============
    "AAOI":  ["applied optoelectronics", "$aaoi"],
    "BABA":  ["alibaba", "$baba"],

    # ============ INDICES ============
    "SPX":   ["s&p 500", "sp500", "spx ", "$spx"],
    "NDX":   ["nasdaq 100", "ndx ", "$ndx"],
    "DJI":   ["dow jones", "djia"],
    "VIX":   ["vix index", " vix ", "$vix"],
    "DXY":   ["dollar index", "dxy "],
    "GOLD":  ["gold price", "xauusd", "gold futures"],
    "OIL":   ["wti crude", "brent crude", "oil price", "crude oil"],
}


# Patrones símbolo agresivos
TICKER_PATTERNS = [
    re.compile(r'\$([A-Z]{2,5})\b'),                       # $TSLA, $BTC
    re.compile(r'#([A-Z]{2,5})\b'),                        # #BTC
    re.compile(r'\bNYSE:\s*([A-Z]{1,5})\b'),               # NYSE: TSLA
    re.compile(r'\bNASDAQ:\s*([A-Z]{1,5})\b'),             # NASDAQ: AAPL
    re.compile(r'\bNYSEARCA:\s*([A-Z]{1,5})\b'),
    re.compile(r'\(([A-Z]{1,5})\)'),                       # (TSLA)
    re.compile(r'\b([A-Z]{2,5})\.(?:PVT|PRIVATE)\b'),      # SPAX.PVT
]


def all_keywords():
    out = {}
    for ticker, kws in TICKERS.items():
        for kw in kws:
            out[kw.lower()] = ticker
    return out


KEYWORD_TO_TICKER = all_keywords()
KNOWN_TICKERS = set(TICKERS.keys())


def detect_tickers_aggressive(text: str) -> list:
    """Detecta tickers usando diccionario + patrones símbolo."""
    if not text:
        return []

    found = []
    seen = set()

    for pattern in TICKER_PATTERNS:
        for m in pattern.finditer(text):
            tk = m.group(1).upper()
            if tk in KNOWN_TICKERS or pattern.pattern.startswith(r'\$') or pattern.pattern.startswith(r'#'):
                if tk not in seen:
                    found.append(tk)
                    seen.add(tk)

    text_lower = text.lower()
    sorted_kws = sorted(KEYWORD_TO_TICKER.keys(), key=len, reverse=True)
    for kw in sorted_kws:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, text_lower):
            ticker = KEYWORD_TO_TICKER[kw]
            if ticker not in seen:
                found.append(ticker)
                seen.add(ticker)

    return found


# Categorización
CRYPTO_SET = {
    "BTC","ETH","SOL","BNB","XRP","ADA","AVAX","DOGE","LINK","POL",
    "DOT","ATOM","NEAR","LTC","BCH","USDT","USDC","DAI","FDUSD","BFUSD","BUSD",
    "TRX","TON","SHIB","PEPE","WIF","BONK","ARB","OP","SUI","APT","ICP","FIL",
    "AAVE","UNI","MKR","HYPE","ZEC","ALLO"
}
CRYPTO_ECOSYSTEM = {"COIN","MSTR","HOOD","RIOT","MARA","CLSK","GLXY","MPAY"}
INDICES = {"SPX","NDX","DJI","VIX","DXY","GOLD","OIL"}


def categorize(tickers: list) -> list:
    """Devuelve categorías [crypto, stocks, macro] según tickers."""
    cats = []
    if any(t in CRYPTO_SET or t in CRYPTO_ECOSYSTEM for t in tickers):
        cats.append("crypto")
    if any(t in INDICES for t in tickers):
        cats.append("macro")
    if any(t not in CRYPTO_SET and t not in CRYPTO_ECOSYSTEM and t not in INDICES
           for t in tickers):
        cats.append("stocks")
    return list(dict.fromkeys(cats))
