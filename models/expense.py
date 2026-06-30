from dataclasses import dataclass

@dataclass
class Expense:
    date: str       # "2026-06-25"
    amount: float   # 5.00
    comment: str    # "a comment"
    category: str   # "Transportation"
    timestamp: str   # "2026-06-25T14:32:10