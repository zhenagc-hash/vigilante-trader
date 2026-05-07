import json
import unittest
from unittest.mock import patch

import vigilante_trader


class BitcoinMarketSystemTests(unittest.TestCase):
    @patch("vigilante_trader.urlopen")
    def test_fetch_bitcoin_market_chart(self, mocked_urlopen):
        mocked_response = mocked_urlopen.return_value.__enter__.return_value
        mocked_response.read.return_value = json.dumps({"prices": [[1, 100.0], [2, 101.0]]}).encode("utf-8")

        payload = vigilante_trader.fetch_bitcoin_market_chart(days="30", vs_currency="usd")

        self.assertEqual(payload["prices"][0][1], 100.0)
        mocked_urlopen.assert_called_once()
        called_url = mocked_urlopen.call_args.args[0]
        self.assertIn("days=30", called_url)
        self.assertIn("vs_currency=usd", called_url)

    def test_analyze_with_100_agents_returns_full_agent_set(self):
        prices = {"prices": [[i, float(100 + i)] for i in range(10)]}

        report = vigilante_trader.analyze_with_100_agents(prices)

        self.assertEqual(report["agent_count"], 100)
        self.assertEqual(len(report["agents"]), 100)
        self.assertIn(report["consensus"], {"bullish", "bearish", "flat"})


if __name__ == "__main__":
    unittest.main()
