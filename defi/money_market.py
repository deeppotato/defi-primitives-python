from dataclasses import dataclass

from datetime import datetime
from typing import List

from defi.token import Token


@dataclass
class MoneyMarket:
    @dataclass
    class Asset:
        token: Token
        supply_shares: dict  # address => share
        total_supply_shares: float
        total_supply_amount: float  # total supply amount for this token
        borrow_shares: dict  # address => share
        total_borrow_shares: float
        total_borrow_amount: float  # total borrow amount for this token

        @property
        def latest_price(self):
            # TODO: get from oracle
            return 1

        def accrue_interest(self, seconds_passed: float):
            utilization = self.total_borrow_amount / self.total_supply_amount
            interest_rate = 0.05  # TODO: calc interest rate using utilization
            seconds_in_year = 365.25 * 24 * 60 * 60
            interest_amount = seconds_passed / seconds_in_year * interest_rate * self.total_borrow_amount
            self.total_borrow_amount += interest_amount
            self.total_supply_amount += interest_amount

    address: str
    assets: List[Asset]  # list of assets available for supply and borrow
    last_interest_update: datetime

    def _accrue_interest(self):
        now = datetime.utcnow()
        seconds_passed = (now - self.last_interest_update).total_seconds()
        for asset in self.assets:
            asset.accrue_interest(seconds_passed)
        self.last_interest_update = now

    def _ltv(self, address):
        supply_value = 0
        borrow_value = 0
        for asset in self.assets:
            supply_amount = asset.supply_shares[address] / asset.total_supply_shares * asset.total_supply_amount
            supply_value += supply_amount * asset.latest_price
            borrow_amount = asset.borrow_shares[address] / asset.total_borrow_shares * asset.total_borrow_amount
            borrow_value += borrow_amount * asset.latest_price
        return borrow_value / supply_value

    def supply(self, sender, asset_id, amount):
        self._accrue_interest()
        asset = self.assets[asset_id]
        asset.token.transfer(sender, self.address, amount)
        share = amount / asset.total_supply_amount * asset.total_supply_shares
        asset.supply_shares[sender] += share
        asset.total_supply_amount += amount
        asset.total_supply_shares += share

    def withdraw(self, sender, asset_id, amount):
        self._accrue_interest()
        asset = self.assets[asset_id]
        asset.token.transfer(self.address, sender, amount)

        share = amount / asset.total_supply_amount
        assert share <= asset.supply_shares[sender]

        asset.supply_shares[sender] -= share
        asset.total_supply_amount -= amount
        asset.total_supply_shares -= share

        assert self._ltv(sender) < 0.7

    def borrow(self, sender, asset_id, amount):
        self._accrue_interest()
        asset = self.assets[asset_id]
        asset.token.transfer(self.address, sender, amount)

        share = amount / asset.total_borrow_amount * asset.total_borrow_shares
        asset.borrow_shares[sender] += share
        asset.total_borrow_amount += amount
        asset.total_borrow_shares += share

        assert self._ltv(sender) < 0.7

    def repay(self, sender, asset_id, amount):
        self._accrue_interest()
        asset = self.assets[asset_id]
        asset.token.transfer(sender, self.address, amount)

        share = amount / asset.total_borrow_amount * asset.total_borrow_shares
        asset.borrow_shares[sender] -= share
        asset.total_borrow_amount -= amount
        asset.total_borrow_shares -= share

    def liquidate(self, address):
        self._accrue_interest()
        assert self._ltv(address) > 0.8
        # TODO: liquidation
