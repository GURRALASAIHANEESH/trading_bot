import pytest
from bot.validators import validate_order_params, ValidationError, OrderParams


class TestValidMarketOrders:

    def test_valid_market_buy(self):
        params = validate_order_params("BTCUSDT", "BUY", "MARKET", 0.01, None)
        assert isinstance(params, OrderParams)
        assert params.symbol == "BTCUSDT"
        assert params.side == "BUY"
        assert params.order_type == "MARKET"
        assert params.quantity == 0.01
        assert params.price is None

    def test_valid_market_sell(self):
        params = validate_order_params("ETHUSDT", "SELL", "MARKET", 0.05, None)
        assert params.side == "SELL"
        assert params.order_type == "MARKET"

    def test_symbol_stripped_and_uppercased(self):
        params = validate_order_params("  btcusdt  ", "BUY", "MARKET", 0.01, None)
        assert params.symbol == "BTCUSDT"

    def test_side_case_insensitive(self):
        params = validate_order_params("BTCUSDT", "buy", "MARKET", 0.01, None)
        assert params.side == "BUY"

    def test_order_type_case_insensitive(self):
        params = validate_order_params("BTCUSDT", "BUY", "market", 0.01, None)
        assert params.order_type == "MARKET"

    def test_market_order_with_price_does_not_raise(self):
        params = validate_order_params("BTCUSDT", "BUY", "MARKET", 0.01, 99999.0)
        assert params.order_type == "MARKET"


class TestValidLimitOrders:

    def test_valid_limit_buy(self):
        params = validate_order_params("BTCUSDT", "BUY", "LIMIT", 0.01, 60000.0)
        assert params.order_type == "LIMIT"
        assert params.price == 60000.0

    def test_valid_limit_sell(self):
        params = validate_order_params("ETHUSDT", "SELL", "LIMIT", 0.05, 2000.0)
        assert params.price == 2000.0
        assert params.side == "SELL"


class TestInvalidSide:

    def test_invalid_side_hold(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_order_params("BTCUSDT", "HOLD", "MARKET", 0.01, None)
        assert "side" in str(exc_info.value)

    def test_invalid_side_long(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_order_params("BTCUSDT", "LONG", "MARKET", 0.01, None)
        assert "side" in str(exc_info.value)

    def test_empty_side(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_order_params("BTCUSDT", "", "MARKET", 0.01, None)
        assert "side" in str(exc_info.value)


class TestInvalidOrderType:

    def test_invalid_order_type_stop(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_order_params("BTCUSDT", "BUY", "STOP", 0.01, None)
        assert "order_type" in str(exc_info.value)

    def test_invalid_order_type_oco(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_order_params("BTCUSDT", "BUY", "OCO", 0.01, None)
        assert "order_type" in str(exc_info.value)

    def test_empty_order_type(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_order_params("BTCUSDT", "BUY", "", 0.01, None)
        assert "order_type" in str(exc_info.value)


class TestInvalidQuantity:

    def test_zero_quantity(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_order_params("BTCUSDT", "BUY", "MARKET", 0.0, None)
        assert "quantity" in str(exc_info.value)

    def test_negative_quantity(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_order_params("BTCUSDT", "BUY", "MARKET", -1.0, None)
        assert "quantity" in str(exc_info.value)


class TestInvalidPrice:

    def test_limit_without_price(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_order_params("BTCUSDT", "BUY", "LIMIT", 0.01, None)
        assert "price" in str(exc_info.value)

    def test_limit_with_zero_price(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_order_params("BTCUSDT", "BUY", "LIMIT", 0.01, 0.0)
        assert "price" in str(exc_info.value)

    def test_limit_with_negative_price(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_order_params("BTCUSDT", "BUY", "LIMIT", 0.01, -500.0)
        assert "price" in str(exc_info.value)


class TestInvalidSymbol:

    def test_empty_symbol(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_order_params("", "BUY", "MARKET", 0.01, None)
        assert "symbol" in str(exc_info.value)

    def test_whitespace_symbol(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_order_params("   ", "BUY", "MARKET", 0.01, None)
        assert "symbol" in str(exc_info.value)


class TestMultipleErrors:

    def test_all_invalid_fields_reported_together(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_order_params("", "INVALID", "INVALID", -1.0, None)
        error_msg = str(exc_info.value)
        assert "symbol" in error_msg
        assert "side" in error_msg
        assert "order_type" in error_msg
        assert "quantity" in error_msg
