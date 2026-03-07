import pytest
from cli import main


class TestCLIValidationErrors:

    def test_invalid_side_returns_code_1(self):
        result = main([
            "--symbol", "BTCUSDT",
            "--side", "HOLD",
            "--order_type", "MARKET",
            "--quantity", "0.01"
        ])
        assert result == 1

    def test_invalid_order_type_returns_code_1(self):
        result = main([
            "--symbol", "BTCUSDT",
            "--side", "BUY",
            "--order_type", "STOP",
            "--quantity", "0.01"
        ])
        assert result == 1

    def test_limit_without_price_returns_code_1(self):
        result = main([
            "--symbol", "BTCUSDT",
            "--side", "BUY",
            "--order_type", "LIMIT",
            "--quantity", "0.01"
        ])
        assert result == 1

    def test_negative_quantity_returns_code_1(self):
        result = main([
            "--symbol", "BTCUSDT",
            "--side", "BUY",
            "--order_type", "MARKET",
            "--quantity", "-5.0"
        ])
        assert result == 1

    def test_zero_quantity_returns_code_1(self):
        result = main([
            "--symbol", "BTCUSDT",
            "--side", "BUY",
            "--order_type", "MARKET",
            "--quantity", "0.0"
        ])
        assert result == 1

    def test_empty_symbol_returns_code_1(self):
        result = main([
            "--symbol", "   ",
            "--side", "BUY",
            "--order_type", "MARKET",
            "--quantity", "0.01"
        ])
        assert result == 1

    def test_limit_with_negative_price_returns_code_1(self):
        result = main([
            "--symbol", "BTCUSDT",
            "--side", "BUY",
            "--order_type", "LIMIT",
            "--quantity", "0.01",
            "--price", "-100.0"
        ])
        assert result == 1

    def test_limit_with_zero_price_returns_code_1(self):
        result = main([
            "--symbol", "BTCUSDT",
            "--side", "SELL",
            "--order_type", "LIMIT",
            "--quantity", "0.01",
            "--price", "0.0"
        ])
        assert result == 1


class TestCLIMissingRequiredArgs:

    def test_missing_symbol_exits(self):
        with pytest.raises(SystemExit) as exc_info:
            main([
                "--side", "BUY",
                "--order_type", "MARKET",
                "--quantity", "0.01"
            ])
        assert exc_info.value.code != 0

    def test_missing_quantity_exits(self):
        with pytest.raises(SystemExit) as exc_info:
            main([
                "--symbol", "BTCUSDT",
                "--side", "BUY",
                "--order_type", "MARKET"
            ])
        assert exc_info.value.code != 0

    def test_missing_side_exits(self):
        with pytest.raises(SystemExit) as exc_info:
            main([
                "--symbol", "BTCUSDT",
                "--order_type", "MARKET",
                "--quantity", "0.01"
            ])
        assert exc_info.value.code != 0

    def test_missing_order_type_exits(self):
        with pytest.raises(SystemExit) as exc_info:
            main([
                "--symbol", "BTCUSDT",
                "--side", "BUY",
                "--quantity", "0.01"
            ])
        assert exc_info.value.code != 0


class TestCLINoAPICall:

    def test_validation_fails_before_api_call(self, mocker):
        mock_client = mocker.patch("cli.get_futures_client")
        main([
            "--symbol", "BTCUSDT",
            "--side", "INVALID",
            "--order_type", "MARKET",
            "--quantity", "0.01"
        ])
        mock_client.assert_not_called()

    def test_client_not_called_on_zero_quantity(self, mocker):
        mock_client = mocker.patch("cli.get_futures_client")
        main([
            "--symbol", "BTCUSDT",
            "--side", "BUY",
            "--order_type", "MARKET",
            "--quantity", "0.0"
        ])
        mock_client.assert_not_called()

    def test_order_not_called_on_client_error(self, mocker):
        from bot.client import BinanceClientError
        mocker.patch("cli.get_futures_client", side_effect=BinanceClientError("bad key"))
        mock_order = mocker.patch("cli.place_order")
        result = main([
            "--symbol", "BTCUSDT",
            "--side", "BUY",
            "--order_type", "MARKET",
            "--quantity", "0.01"
        ])
        mock_order.assert_not_called()
        assert result == 2
