import csv
from pathlib import Path
from typing import ClassVar

from models.expense import Expense


class ExpenseRepository:

    FIELDNAMES: ClassVar[list[str]] = [
        "Date", "Amount", "Comment", "Category", "Timestamp", "EntryMode", "Mileage", "Rate"
    ]

    def __init__(self, path: str = "PaloVerdeRentalExpense.csv") -> None:
        project_root = Path(__file__).resolve().parent.parent
        self.path = project_root / "data" / path

    def load_all(self):
        if not self.path.exists():
            return []

        expenses = []
        with self.path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                expenses.append(
                    Expense(
                        date=row["Date"],
                        amount=float(row["Amount"]),
                        comment=row["Comment"],
                        category=row["Category"],
                        timestamp=row["Timestamp"], 
                        entry_mode = row["EntryMode"], 
                        mileage = float(row["Mileage"]) if row["Mileage"] else None,
                        rate = float(row["Rate"]) if row["Rate"] else None,
                    )
                )
        return expenses

    def save_all(self, expenses):
        with self.path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.FIELDNAMES)
            for exp in expenses:
                writer.writerow(self._row(exp))
                    

    def add(self, expense: Expense):
        file_exists = self.path.exists()

        with self.path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            if not file_exists:
                writer.writerow(self.FIELDNAMES)
            writer.writerow(self._row(expense))


    def _row(self, exp: Expense):
        return [
            exp.date, exp.amount, exp.comment, exp.category, exp.timestamp,
            exp.entry_mode,
            exp.mileage if exp.mileage is not None else "",
            exp.rate if exp.rate is not None else "",
        ]
    

    def update(self, updated: Expense):
        expenses = self.load_all()

        for i, exp in enumerate(expenses):
            if exp.timestamp == updated.timestamp:
                expenses[i] = updated
                break

        self.save_all(expenses)

    def delete_by_timestamp(self, timestamp: str):
        expenses = self.load_all()
        expenses = [exp for exp in expenses if exp.timestamp != timestamp]
        self.save_all(expenses)
