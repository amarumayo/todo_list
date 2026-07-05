import csv
from pathlib import Path
from models.expense import Expense

class ExpenseRepository:
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
                        timestamp=row["Timestamp"]
                    )
                )
        return expenses

    def save_all(self, expenses):
        with self.path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Amount", "Comment", "Category", "Timestamp"])
            for exp in expenses:
                writer.writerow([
                    exp.date,
                    exp.amount,
                    exp.comment,
                    exp.category,
                    exp.timestamp
                ])

    def add(self, expense: Expense):
        file_exists = self.path.exists()

        with self.path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            if not file_exists:
                writer.writerow(["Date", "Amount", "Comment", "Category", "Timestamp"])

            writer.writerow([
                expense.date,
                expense.amount,
                expense.comment,
                expense.category,
                expense.timestamp
            ])

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
