
import sqlite3
from pathlib import Path
from models.expense import Expense


class ExpenseRepositoryDB:
    def __init__(self, path: str = "expense.db"):
        project_root = Path(__file__).resolve().parent.parent
        self.path = project_root / "data" / path
        self.conn = sqlite3.connect(self.path)
        self._create_table()


    def _create_table(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT NOT NULL,
                amount      REAL NOT NULL,
                comment     TEXT NOT NULL,
                category    TEXT NOT NULL,
                timestamp   TEXT NOT NULL,
                entry_mode  TEXT NOT NULL DEFAULT 'Amount',
                mileage     REAL,
                rate        REAL
            )
            """
        )
        self.conn.commit()

    def load_all(self):
        cursor = self.conn.execute(
            "SELECT id, date, amount, comment, category, timestamp, entry_mode, mileage, rate "
            "FROM expenses"
        )
        return [
            Expense(
                date=row[1],
                amount=row[2],
                comment=row[3],
                category=row[4],
                timestamp=row[5],
                id=row[0],
                entry_mode=row[6],
                mileage=row[7],
                rate=row[8],
            )
            for row in cursor.fetchall()
        ]

    def add(self, expense: Expense):

        cursor = self.conn.execute(
            """
            INSERT INTO expenses
                (date, amount, comment, category, timestamp, entry_mode, mileage, rate)
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?) 
            """, 
            (
                expense.date, expense.amount, expense.comment, expense.category,
                expense.timestamp, expense.entry_mode, expense.mileage, expense.rate      
            )  
        ) 
        self.conn.commit()
        return cursor.lastrowid

    def update(self, updated: Expense):
        self.conn.execute(
            """
            UPDATE expenses
            SET date = ?, amount = ?, comment = ?, category = ?,
                entry_mode = ?, mileage = ?, rate = ?
            WHERE id = ?
            """,
            (updated.date, updated.amount, updated.comment, updated.category,
            updated.entry_mode, updated.mileage, updated.rate, updated.id

            )
        )
        self.conn.commit()





        

