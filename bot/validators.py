from dataclasses import dataclass
from typing import Optional


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


class ValidationError(Exception):
    pass


@dataclass
class OrderParams:
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float]


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float],
) -> OrderParams:
    errors: list[str] = []

    if not symbol or not symbol.strip():
        errors.append("'symbol' must be a non-empty string (e.g., BTCUSDT).")

    side_upper = side.upper() if side else ""
    if side_upper not in VALID_SIDES:
        errors.append(f"'side' must be BUY or SELL, got: '{side}'.")

    order_type_upper = order_type.upper() if order_type else ""
    if order_type_upper not in VALID_ORDER_TYPES:
        errors.append(f"'order_type' must be MARKET or LIMIT, got: '{order_type}'.")

    if quantity <= 0:
        errors.append(f"'quantity' must be a positive float, got: {quantity}.")

    if order_type_upper == "LIMIT":
        if price is None:
            errors.append("'price' is required for LIMIT orders.")
        elif price <= 0:
            errors.append(f"'price' must be positive for LIMIT orders, got: {price}.")

    if errors:
        raise ValidationError("\n  ".join(["Validation failed:"] + errors))

    return OrderParams(
        symbol=symbol.strip().upper(),
        side=side_upper,
        order_type=order_type_upper,
        quantity=quantity,
        price=price,
    )
