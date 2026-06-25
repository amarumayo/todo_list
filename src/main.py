import sys
from PyQt6.QtCore import QDate, Qt
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
    QTableWidgetItem
)
from data.expense_repository import ExpenseRepository
from models.expense import Expense



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

        # expense table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            'Date', 'Amount', 'Comment', 'Category'
        ])
        self.table.setSortingEnabled(True)
        self.load_expenses_from_csv()

        # add form, button and table to main layout
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.submit_button)
        main_layout.addWidget(self.table)
        self.setCentralWidget(central)

        # connect events
        self.submit_button.clicked.connect(self.on_submit_button_push)


    def on_submit_button_push(self):
        # extract data
        date = self.date_input.date().toString("yyyy-MM-dd")
        amount = self.amount_input.text()
        comment = self.comment_input.text()
        category = self.category_input.currentText()

        expense = Expense(
            date = date, 
            amount = float(amount), 
            comment = comment, 
            category=category
        )

        # add to csv, table
        self.expense_repo.add(expense)
        self.add_expense_to_ui_table(expense)

        # sort the new table data 
        self.sort_table_by_date()   
        self.clear_form()
            
        
    def add_expense_to_ui_table(self, expense: Expense):
        this_row = self.table.rowCount()
        self.table.insertRow(this_row)

        self.table.setItem(this_row, 0, QTableWidgetItem(expense.date))
        self.table.setItem(this_row, 1, QTableWidgetItem(str(expense.amount)))
        self.table.setItem(this_row, 2, QTableWidgetItem(expense.comment))
        self.table.setItem(this_row, 3, QTableWidgetItem(expense.category))


    def sort_table_by_date(self):
        self.table.sortItems(0, order=Qt.SortOrder.DescendingOrder)


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