import sys
from datetime import date
from PyQt6.QtCore import (
    QDate, 
    Qt, 
    QTimer
)
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QWidget, 
    QVBoxLayout, 
    QFormLayout, 
    QLineEdit, 
    QPushButton, 
    QComboBox,
    QDateEdit,
    QTableWidget, 
    QTableWidgetItem,
    QMessageBox
)
from data.expense_repository import ExpenseRepository
from models.expense import Expense
from datetime import datetime
from src.enums import ExpenseColumns



class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.expense_repo = ExpenseRepository()

        self.setWindowTitle("test")
        self.setMinimumSize(500, 300)

        # central widget and main layout
        central = QWidget(self)
        main_layout = QVBoxLayout(central)

        # form layout for inputs
        form_layout = QFormLayout()

        # inputs
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form_layout.addRow("Date:", self.date_input)

        self.amount_input = QLineEdit()
        form_layout.addRow("Amount:", self.amount_input)

        self.comment_input = QLineEdit()
        form_layout.addRow("Comment:", self.comment_input)

        self.category_input = QComboBox()
        self.category_input.addItems([
            'Transportation',
            'Supplies',
            'Labor',
        ])
        form_layout.addRow("Category:", self.category_input)

        # button
        self.submit_button = QPushButton("Add Expense")   
        self.submit_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2d89ef;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1b5fbd;
            }
            QPushButton:pressed {
                background-color: #164a94;
            }
            """
        ) 

        # expense table
        self.table = QTableWidget()
        self.table.setColumnCount(len(ExpenseColumns))
        self.table.setHorizontalHeaderLabels([
            'Date', 'Amount', 'Comment', 'Category', 'Timestamp'
        ])
        # hide the timestamp column - its used only for internal sorting
        self.table.setColumnHidden(ExpenseColumns.TIMESTAMP, True)

        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            """
            QTableWidget {
            background-color: white;
            alternate-background-color: #f0f0f0;
            }
            """
        )

        self.load_expenses_from_csv()

        # add form, button and table to main layout
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.submit_button)
        main_layout.addWidget(self.table)
        self.setCentralWidget(central)

        # connect events
        self.submit_button.clicked.connect(self.on_submit_button_push)


    def on_submit_button_push(self):
        
        is_valid, error_message = self.validate_inputs()

        if not is_valid:             
            self.show_error(error_message)
            return


        # extract data
        date = self.date_input.date().toString("yyyy-MM-dd")
        amount = self.amount_input.text()
        comment = self.comment_input.text()
        category = self.category_input.currentText()
        timestamp = datetime.now().isoformat(timespec="seconds")

        expense = Expense(
            date=date, 
            amount=float(amount), 
            comment=comment, 
            category=category,
            timestamp=timestamp
        )
        
        # add to csv, table
        self.expense_repo.add(expense)
        self.add_expense_to_ui_table(expense)

        # sort 
        self.sort_table_by_date()

        self.clear_form()
    
    

    def validate_inputs(self):

        amount_text = self.amount_input.text().strip()
        comment_text = self.comment_input.text().strip()
        selected_date = self.date_input.date().toPyDate()

        # date cannot be in the future
        today = date.today()
        if selected_date > today:
            return False, "Date cannot be in the future."

        # amount must be numeric
        try:
            amount_value = float(amount_text)
        except ValueError:
            return False, "Amount must be a number."

        # amount must be positive
        if amount_value <= 0:
            return False, "Amount must be greater than zero."

        # comment must not be empty
        if not comment_text:
            return False, "Comment cannot be empty."

        return True, ""


    def show_error(self, message: str):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("Invalid Input")
        box.setText(message)
        box.exec()
        
            
        
    def add_expense_to_ui_table(self, expense: Expense):
        self.table.setSortingEnabled(False)
        
        this_row = self.table.rowCount()
        self.table.insertRow(this_row)

        self.table.setItem(
            this_row, ExpenseColumns.DATE, QTableWidgetItem(expense.date)
        )
        self.table.setItem(
            this_row, ExpenseColumns.AMOUNT, QTableWidgetItem(f"${expense.amount:,.2f}")
        )
        self.table.setItem(
            this_row, ExpenseColumns.COMMENT, QTableWidgetItem(expense.comment)
        )
        self.table.setItem(
            this_row, ExpenseColumns.CATEGORY, QTableWidgetItem(expense.category)
        )
        self.table.setItem(
            this_row, ExpenseColumns.TIMESTAMP, QTableWidgetItem(expense.timestamp)
        )

        self.table.setSortingEnabled(True)

    def sort_table_by_date(self):
        self.table.sortItems(
            ExpenseColumns.TIMESTAMP, order=Qt.SortOrder.DescendingOrder)


    def clear_form(self):
        self.date_input.setDate(QDate.currentDate())
        self.amount_input.clear()
        self.comment_input.clear()
        self.category_input.setCurrentIndex(0)


    def load_expenses_from_csv(self):

        rows = self.expense_repo.load_all()

        for expense in rows:
            self.add_expense_to_ui_table(expense)
        
        self.sort_table_by_date()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()