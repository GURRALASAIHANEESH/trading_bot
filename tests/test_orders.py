import pytest
from bot.orders import _safe_avg_price


class TestSafeAvgPrice:

    def test_valid_avg_price_returned_directly(self):
        response = {"avgPrice": "68461.40000"}
        assert _safe_avg_price(response) == "68461.40000"

    def test_zero_avg_price_computes_from_cum_quote(self):
        response = {
            "avgPrice": "0",
            "cumQuote": "684.61",
            "executedQty": "0.01",
        }
        result = _safe_avg_price(response)
        assert "computed" in result
        assert "68461" in result

    def test_zero_avg_price_falls_back_to_order_price(self):
        response = {
            "avgPrice": "0",
            "cumQuote": "0",
            "executedQty": "0",
            "price": "80000.0",
        }
        result = _safe_avg_price(response)
        assert "order price" in result
        assert "80000" in result

    def test_all_zero_returns_na(self):
        response = {
            "avgPrice": "0",
            "cumQuote": "0",
            "executedQty": "0",
            "price": "0",
        }
        assert _safe_avg_price(response) == "N/A"

    def test_empty_response_returns_na(self):
        assert _safe_avg_price({}) == "N/A"

    def test_missing_avg_price_key_falls_back(self):
        response = {
            "cumQuote": "100.0",
            "executedQty": "0.05",
        }
        result = _safe_avg_price(response)
        assert "computed" in result

    def test_string_zero_avg_price_treated_as_zero(self):
        response = {
            "avgPrice": "0.00000000",
            "cumQuote": "0",
            "executedQty": "0",
            "price": "",
        }
        assert _safe_avg_price(response) == "N/A"

    def test_eth_avg_price_returned(self):
        response = {"avgPrice": "1976.01000"}
        assert _safe_avg_price(response) == "1976.01000"
