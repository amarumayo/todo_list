from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QComboBox,
    QDateEdit,
    QTableWidget,
)
from PyQt6.QtCore import QDate, Qt
from src.enums import ExpenseColumns


class ExpenseUI:
    def __init__(self, window):
        self.window = window
        self.form_layout = self.build_form()
        self.buttons = self.build_buttons()
        self.table = self.build_table()
        self.assemble_layout()


    def build_form(self):
        form = QFormLayout()

        self.window.date_input = QDateEdit()
        self.window.date_input.setCalendarPopup(True)
        self.window.date_input.setDate(QDate.currentDate())
        form.addRow("Date:", self.window.date_input)
        
        self.window.amount_input = QLineEdit()            
        form.addRow("Amount:", self.window.amount_input)
        
        self.window.comment_input = QLineEdit()
        form.addRow("Comment:", self.window.comment_input)

        self.window.category_input = QComboBox()
        self.window.category_input.addItems(["Transportation", "Supplies", "Labor"])
        form.addRow("Category:", self.window.category_input)

        return form

    def build_buttons(self):

        # submit
        self.window.submit_button = QPushButton("Add Expense")
        self.window.submit_button.setStyleSheet(
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

        self.window.delete_button = QPushButton("Delete Expense")
        self.window.delete_button.setStyleSheet(
            """
            QPushButton {
                background-color: #d9534f;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #c9302c; }
            QPushButton:pressed { background-color: #ac2925; }
            """
        )

        return self.window.submit_button, self.window.delete_button

    def build_table(self):
        table = QTableWidget()
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setColumnCount(len(ExpenseColumns))
        table.setHorizontalHeaderLabels(
            ["Date", "Amount", "Comment", "Category", "Timestamp"]
        )

        # timestamp column hidden
        table.setColumnHidden(ExpenseColumns.TIMESTAMP, True)
        table.setSortingEnabled(True)
        table.setAlternatingRowColors(True)
        self.window.table = table
        return table

    def assemble_layout(self):
        central = QWidget(self.window)
        layout = QVBoxLayout(central)

        layout.addLayout(self.form_layout)

        submit_button, delete_button = self.build_buttons()
        layout.addWidget(submit_button)
        layout.addWidget(delete_button)

        layout.addWidget(self.table)
    
        self.window.setCentralWidget(central)












