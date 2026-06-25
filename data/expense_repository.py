from pathlib import Path
import csv
from models.expense import Expense



class ExpenseRepository:
    def __init__(self, path: str = "PaloVerdeRentalExpense.csv") -> None:
        project_root = Path(__file__).resolve().parent.parent
        self.path = project_root / "data" / path

    def add(self, expense: Expense) -> None:
        file_exists = self.path.exists()

        with self.path.open(
            mode="a",
            newline="",
            encoding="utf-8"
        ) as f:
            writer = csv.writer(f)

            if not file_exists:
                writer.writerow(["Date", "Amount", "Comment", "Category"])

            writer.writerow([
                expense.date, 
                expense.amount, 
                expense.comment, 
                expense.category
            ])

    def load_all(self):
       
        if not self.path.exists():
            return [] # No file yet, nothing to load

        expenses = []

        with self.path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                expense = Expense(
                    date = row["Date"],
                    amount = float(row["Amount"]),
                    comment = row["Comment"],
                    category=row["Category"]
                )
                expenses.append(expense)
        return expenses


