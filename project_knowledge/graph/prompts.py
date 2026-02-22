"""Domain-specific extraction prompts for LLM-based entity extraction."""

ENTITY_EXTRACTION_PROMPT = """
Extract trading-relevant entities from this text. Return JSON only.

ENTITY TYPES (use exactly these labels):
- Ticker: Stock symbols (NVDA, AAPL, MSFT)
- Company: Company names (NVIDIA, Apple Inc, Microsoft)
- Executive: Named executives with titles (Jensen Huang CEO)
- Analyst: Named analysts with firms (Dan Ives Wedbush)
- Product: Products/services (Blackwell GPU, iPhone, Azure)
- Catalyst: Events that move stock price (earnings beat, FDA approval, product launch)
- Sector: Market sectors (Technology, Healthcare, Financials)
- Industry: Specific industries (Semiconductors, Cloud Computing, Biotechnology)
- Pattern: Trading patterns (gap and go, earnings drift, mean reversion)
- Bias: Cognitive biases (loss aversion, confirmation bias, recency bias)
- Strategy: Trading strategies (earnings momentum, breakout, swing trade)
- Structure: Trade structures (bull call spread, iron condor, shares)
- Risk: Identified risks (concentration risk, macro exposure, execution risk)
- Signal: Trading signals (RSI oversold, volume breakout, MACD cross)
- EarningsEvent: Quarterly/annual reports (Q4 2025, FY 2025)
- MacroEvent: Macro events (Fed rate decision, CPI release, tariff announcement)
- Timeframe: Time horizons (intraday, swing, position)
- FinancialMetric: Metrics (revenue growth, gross margin, EPS)

TEXT:
{text}

Return JSON array:
[{{"type": "...", "value": "...", "confidence": 0.0-1.0, "evidence": "quote from text"}}]

Rules:
- Only extract entities EXPLICITLY mentioned in the text
- Do NOT infer entities not directly stated
- Confidence should reflect how clearly the entity is identified
- Evidence must be a direct quote from the text
"""

RELATION_EXTRACTION_PROMPT = """
Given these entities extracted from a trading document, identify relationships between them.

ENTITIES:
{entities_json}

RELATIONSHIP TYPES (use exactly these):
- ISSUED: Company issued Ticker
- IN_SECTOR: Company belongs to Sector
- IN_INDUSTRY: Company belongs to Industry
- MAKES: Company makes Product
- LEADS: Executive leads Company
- COMPETES_WITH: Company competes with Company
- SUPPLIES_TO: Company supplies to Company
- CUSTOMER_OF: Company is customer of Company
- CORRELATED_WITH: Ticker correlates with Ticker
- COVERS: Analyst covers Ticker
- AFFECTED_BY: Ticker affected by Catalyst
- EXPOSED_TO: Ticker exposed to MacroEvent
- HAS_EARNINGS: Ticker has EarningsEvent
- THREATENS: Risk threatens Ticker
- WORKS_FOR: Strategy works for Ticker
- USES: Strategy uses Structure
- DETECTED_IN: Bias detected in Trade
- OBSERVED_IN: Pattern observed in Ticker
- INDICATES: Signal indicates Ticker
- DERIVED_FROM: Learning derived from Trade
- ADDRESSES: Learning addresses Bias
- UPDATES: Learning updates Strategy
- MITIGATED_BY: Risk mitigated by Strategy
- ANALYZES: Analysis analyzes Ticker
- MENTIONS: Analysis mentions (any entity)
- BASED_ON: Trade based on Analysis
- TRADED: Trade traded Ticker

SOURCE TEXT:
{text}

Return JSON array:
[{{"from": {{"type": "...", "value": "..."}}, "relation": "...", "to": {{"type": "...", "value": "..."}}, "confidence": 0.0-1.0, "evidence": "quote"}}]

Rules:
- Only extract relationships explicitly stated or strongly implied
- Do NOT infer weak or speculative connections
- Confidence should reflect how clearly the relationship is stated
"""

# Shorter prompt for specific entity types
TICKER_EXTRACTION_PROMPT = """
Extract stock ticker symbols from this text. Return JSON array.

TEXT:
{text}

Return only ticker symbols found:
[{{"type": "Ticker", "value": "SYMBOL", "confidence": 0.9, "evidence": "quote"}}]
"""

BIAS_EXTRACTION_PROMPT = """
Extract cognitive biases mentioned in this trading text. Return JSON array.

Common trading biases:
- Loss aversion, Confirmation bias, Recency bias, Anchoring
- FOMO, Overconfidence, Hindsight bias, Sunk cost fallacy

TEXT:
{text}

Return:
[{{"type": "Bias", "value": "bias name", "confidence": 0.8, "evidence": "quote"}}]
"""
