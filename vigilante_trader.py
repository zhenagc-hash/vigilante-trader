import json
from dataclasses import dataclass
from statistics import fmean
from typing import Any
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
    with urlopen(f"{COINGECKO_MARKET_CHART_URL}?{query}", timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


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


def analyze_with_100_agents(market_chart: dict[str, Any], agent_count: int = 100) -> dict[str, Any]:
    if agent_count <= 0:
        raise ValueError("agent_count must be positive")

    prices = _extract_prices(market_chart)
    if not prices:
        analyses = [AgentAnalysis(agent_id=i + 1, average_price=0.0, trend="flat") for i in range(agent_count)]
    else:
        analyses: list[AgentAnalysis] = []
        chunk_size = max(1, len(prices) // agent_count)
        for i in range(agent_count):
            start = i * chunk_size
            chunk = prices[start : start + chunk_size] or [prices[-1]]
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
        "consensus": max(trend_counts, key=trend_counts.get),
        "trend_counts": trend_counts,
    }


def build_bitcoin_market_system(days: str = "max", vs_currency: str = "usd", agent_count: int = 100) -> dict[str, Any]:
    market_chart = fetch_bitcoin_market_chart(days=days, vs_currency=vs_currency)
    analysis = analyze_with_100_agents(market_chart, agent_count=agent_count)
    return {
        "source": "CoinGecko",
        "days": days,
        "vs_currency": vs_currency,
        "price_points": len(market_chart.get("prices", [])),
        "analysis": analysis,
    }


if __name__ == "__main__":
    print(json.dumps(build_bitcoin_market_system(), indent=2))
