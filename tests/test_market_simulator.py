from datetime import datetime, timezone

from backend.market_simulator import simulated_price

T = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_price_is_deterministic():
    assert simulated_price("AAPL", T) == simulated_price("AAPL", T)


def test_price_is_positive():
    for ticker in ("AAPL", "TSLA", "SPY", "BTC"):
        assert simulated_price(ticker, T) > 0


def test_tickers_have_different_prices():
    prices = {simulated_price(t, T) for t in ("AAPL", "TSLA", "SPY", "NVDA")}
    assert len(prices) > 1