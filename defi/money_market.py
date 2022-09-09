from dataclasses import dataclass

from defi.token import Token


@dataclass
class MoneyMarket:
    address: str
    token: Token
    pool_token: Token

    def supply(self, sender, amount):
        if self.pool_token.total_supply == 0:
            # first time liquidity is supplied
            self.token.transfer(sender, self.address, amount)
            self.pool_token.mint(sender, 1)
            return

        balance = self.token.balances[self.address]
        mint_pool_token = amount / balance * self.pool_token.total_supply

        self.token.transfer(sender, self.address, amount)
        self.pool_token.mint(sender, mint_pool_token)

    def withdraw(self):
        pass

    def borrow(self):
        pass

    def repay(self, sender, amount):
        pass
