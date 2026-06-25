from dataclasses import dataclass

@dataclass
class Expense:
    date: str
    amount: float
    comment: str
    category: str