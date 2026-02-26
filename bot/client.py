import logging
import os
from typing import Optional

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("trading_bot.client")

FUTURES_DEMO_BASE_URL = "https://demo-fapi.binance.com"


class BinanceClientError(Exception):
    pass


def get_futures_client() -> Client:
    api_key: Optional[str] = os.getenv("BINANCE_API_KEY")
    api_secret: Optional[str] = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        raise BinanceClientError(
            "BINANCE_API_KEY and BINANCE_API_SECRET must be set "
            "in your .env file."
        )

    logger.info("Initialising Binance Futures Demo client.")

    try:
        client = Client(
            api_key=api_key,
            api_secret=api_secret,
            testnet=False,
        )

        # Override futures REST base URL to demo endpoint
        client.FUTURES_URL = FUTURES_DEMO_BASE_URL + "/fapi"

        logger.info(
            "Binance client initialised. Base URL: %s", FUTURES_DEMO_BASE_URL
        )
        return client

    except BinanceAPIException as exc:
        logger.exception("Binance API error during client setup: %s", exc)
        raise BinanceClientError(
            f"Failed to initialise Binance client: {exc}"
        ) from exc

    except BinanceRequestException as exc:
        logger.exception("Binance request error during client setup: %s", exc)
        raise BinanceClientError(
            f"Failed to initialise Binance client: {exc}"
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected error during client setup: %s", exc)
        raise BinanceClientError(
            f"Unexpected error initialising Binance client: {exc}"
        ) from exc
