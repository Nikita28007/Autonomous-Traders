import pytest

from backend.accounts import INITIAL_BALANCE, SPREAD, Account


def test_buy_applies_spread(fixed_price):
    acc = Account.get("test")
    acc.buy_shares("AAPL", 10, "test")
    assert acc.holdings == {"AAPL": 10}
    assert acc.balance == pytest.approx(INITIAL_BALANCE - 100.0 * (1 + SPREAD) * 10)


def test_round_trip_loses_spread(fixed_price):
    acc = Account.get("test")
    acc.buy_shares("AAPL", 10, "in")
    acc.sell_shares("AAPL", 10, "out")
    assert acc.holdings == {}
    assert acc.balance == pytest.approx(INITIAL_BALANCE - 2 * SPREAD * 100.0 * 10)


def test_buy_with_insufficient_funds_raises(fixed_price):
    acc = Account.get("test")
    with pytest.raises(ValueError, match="Insufficient funds"):
        acc.buy_shares("AAPL", 1000, "too much")


def test_sell_more_than_held_raises(fixed_price):
    acc = Account.get("test")
    acc.buy_shares("AAPL", 1, "one")
    with pytest.raises(ValueError, match="Not enough shares"):
        acc.sell_shares("AAPL", 2, "too many")


def test_account_persists_between_loads(fixed_price):
    Account.get("test").buy_shares("AAPL", 3, "persist")
    assert Account.get("test").holdings == {"AAPL": 3}


def test_reset_restores_initial_state(fixed_price):
    acc = Account.get("test")
    acc.buy_shares("AAPL", 3, "x")
    acc.reset("new strategy")
    assert acc.balance == INITIAL_BALANCE
    assert acc.holdings == {} and acc.transactions == []
    assert acc.strategy == "new strategy"