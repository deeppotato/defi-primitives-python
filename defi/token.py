from dataclasses import dataclass


@dataclass
class Token:
    balances: dict  # address -> amount
    symbol: str

    @property
    def total_supply(self):
        return sum(self.balances.values())

    def transfer(self, src: str, dst: str, amount: float):
        assert self.balances[src] >= amount
        self.balances[src] -= amount
        if dst not in self.balances:
            self.balances[dst] = 0
        self.balances[dst] += amount

    def mint(self, addr: str, amount: float):
        if addr not in self.balances:
            self.balances[addr] = 0
        self.balances[addr] += amount

    def burn(self, addr: str, amount: float):
        self.balances[addr] -= amount
