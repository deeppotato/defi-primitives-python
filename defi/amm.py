from dataclasses import dataclass

from defi.token import Token


@dataclass
class AMMPool:
    address: str
    a: Token
    b: Token
    lp_token: Token

    def add_liquidity(self, sender: str, a_amount: float, b_amount: float):
        if self.lp_token.total_supply == 0:
            # first time liquidity is added
            self.a.transfer(sender, self.address, a_amount)
            self.b.transfer(sender, self.address, b_amount)
            self.lp_token.mint(sender, 1)
            return

        a_balance = self.a.balances[self.address]
        b_balance = self.b.balances[self.address]
        price = a_balance / b_balance

        if a_amount / price >= b_amount:
            # more a than b
            add_a = price * b_amount
            add_b = b_amount
        else:
            # more b than a
            add_a = a_amount
            add_b = a_amount / price

        mint_lp_tokens = add_a / a_balance * self.lp_token.total_supply
        self.a.transfer(sender, self.address, add_a)
        self.b.transfer(sender, self.address, add_b)
        self.lp_token.mint(sender, mint_lp_tokens)

    def remove_liquidity(self, sender: str, lp_token_amount: float):
        assert self.lp_token.balances[sender] >= lp_token_amount
        lp_share = lp_token_amount / self.lp_token.total_supply
        remove_a_amount = lp_share * self.a.balances[self.address]
        remove_b_amount = lp_share * self.b.balances[self.address]
        self.a.transfer(self.address, sender, remove_a_amount)
        self.b.transfer(self.address, sender, remove_b_amount)
        self.lp_token.burn(sender, lp_token_amount)

    def swap_a_to_b(self, sender: str, amount_in: float):
        a_balance = self.a.balances[self.address]
        b_balance = self.b.balances[self.address]
        k = a_balance * b_balance

        new_b_balance = k / (a_balance + amount_in)
        b_amount_out = b_balance - new_b_balance

        self.a.transfer(sender, self.address, amount_in)
        self.b.transfer(self.address, sender, b_amount_out)
        assert k >= self.a.balances[self.address] * self.b.balances[self.address]

    def swap_b_to_a(self, sender: str, amount_in: float):
        a_balance = self.a.balances[self.address]
        b_balance = self.b.balances[self.address]
        k = a_balance * b_balance

        new_a_balance = k / (b_balance + amount_in)
        a_amount_out = a_balance - new_a_balance

        self.b.transfer(sender, self.address, amount_in)
        self.a.transfer(self.address, sender, a_amount_out)
        assert k >= self.a.balances[self.address] * self.b.balances[self.address]

    def __repr__(self):
        a_balance = self.a.balances.get(self.address) or 0
        b_balance = self.b.balances.get(self.address) or 0
        k = a_balance * b_balance
        price = round(b_balance/a_balance, 2) if a_balance != 0 else 'N/A'
        return f'a={a_balance} b={b_balance} k={k} price={price} lp_token={self.lp_token.total_supply}'


def example():
    user_addr = '0xUser'
    a = Token(balances={user_addr: 100}, symbol='ATOM')
    b = Token(balances={user_addr: 100}, symbol='USDC')
    lp_token = Token(balances={}, symbol='ATOM-USDC LP')
    amm = AMMPool(
        address='0xContract',
        a=a,
        b=b,
        lp_token=lp_token,
    )
    print(amm)

    amm.add_liquidity(user_addr, 1, 15)
    print(amm)

    amm.swap_a_to_b(user_addr, 0.1)
    print(amm)

    amm.add_liquidity(user_addr, 1, 15)
    print(amm)

    amm.swap_a_to_b(user_addr, 0.1)
    print(amm)


example()
