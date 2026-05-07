import json
from dataclasses import dataclass
from statistics import fmean
from typing import Any
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

COINGECKO_MARKET_CHART_URL = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"


@dataclass(frozen=True)
class AgentAnalysis:
    agent_id: int
    average_price: float
    trend: str


def fetch_bitcoin_market_chart(days: str = "max", vs_currency: str = "usd") -> dict[str, Any]:
    query = urlencode({"vs_currency": vs_currency, "days": days})
    try:
        with urlopen(f"{COINGECKO_MARKET_CHART_URL}?{query}", timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except URLError as error:
        raise RuntimeError("Failed to fetch Bitcoin market chart data from CoinGecko") from error


def _extract_prices(market_chart: dict[str, Any]) -> list[float]:
    return [float(point[1]) for point in market_chart.get("prices", []) if len(point) >= 2]


def _classify_trend(prices: list[float]) -> str:
    if len(prices) < 2:
        return "flat"
    if prices[-1] > prices[0]:
        return "bullish"
    if prices[-1] < prices[0]:
        return "bearish"
    return "flat"


def _consensus_from_counts(trend_counts: dict[str, int]) -> str:
    priorities = {"bullish": 2, "flat": 1, "bearish": 0}
    return max(trend_counts, key=lambda trend: (trend_counts[trend], priorities[trend]))


def analyze_with_agents(market_chart: dict[str, Any], agent_count: int = 100) -> dict[str, Any]:
    if agent_count <= 0:
        raise ValueError("agent_count must be positive")

    prices = _extract_prices(market_chart)
    if not prices:
        analyses = [AgentAnalysis(agent_id=i + 1, average_price=0.0, trend="flat") for i in range(agent_count)]
    else:
        analyses: list[AgentAnalysis] = []
        chunk_size = len(prices) // agent_count
        remainder = len(prices) % agent_count
        offset = 0
        for i in range(agent_count):
            current_chunk_size = chunk_size + (1 if i < remainder else 0)
            start = offset
            end = start + current_chunk_size
            chunk = prices[start:end] if current_chunk_size > 0 else [prices[-1]]
            offset = end
            analyses.append(
                AgentAnalysis(
                    agent_id=i + 1,
                    average_price=round(fmean(chunk), 2),
                    trend=_classify_trend(chunk),
                )
            )

    trend_counts = {
        "bullish": sum(1 for item in analyses if item.trend == "bullish"),
        "bearish": sum(1 for item in analyses if item.trend == "bearish"),
        "flat": sum(1 for item in analyses if item.trend == "flat"),
    }

    return {
        "agent_count": agent_count,
        "agents": [item.__dict__ for item in analyses],
        "consensus": _consensus_from_counts(trend_counts),
        "trend_counts": trend_counts,
    }


def build_bitcoin_market_system(days: str = "max", vs_currency: str = "usd", agent_count: int = 100) -> dict[str, Any]:
    market_chart = fetch_bitcoin_market_chart(days=days, vs_currency=vs_currency)
    analysis = analyze_with_agents(market_chart, agent_count=agent_count)
    return {
        "source": "CoinGecko",
        "days": days,
        "vs_currency": vs_currency,
        "price_points": len(market_chart.get("prices", [])),
        "analysis": analysis,
    }


if __name__ == "__main__":
    try:
        print(json.dumps(build_bitcoin_market_system(), indent=2))
    except RuntimeError as error:
        print(json.dumps({"error": str(error)}, indent=2))
