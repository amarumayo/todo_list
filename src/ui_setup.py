from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QComboBox,
    QDateEdit,
    QTableWidget,
    QLabel
)
from PyQt6.QtCore import QDate, Qt
from src.enums import ExpenseColumns


class ExpenseUI:
    def __init__(self, parent):
        self.parent = parent

        # Explicit widget attributes
        self.entry_mode_input: QComboBox | None = None
        self.date_input: QDateEdit | None = None
        self.amount_input: QLineEdit | None = None
        self.comment_input: QLineEdit | None = None
        self.category_input: QComboBox | None = None
        self.mileage_input: QLineEdit | None = None
        self.rate_input: QLineEdit | None = None
        self.table: QTableWidget | None = None
        self.submit_button: QPushButton | None = None
        self.delete_button: QPushButton | None = None
        
        self.form_layout = self.build_form()
        self.submit_button, self.delete_button = self.build_buttons()
        self.table = self.build_table()
        self.assemble_layout()


    def build_form(self):
        form = QFormLayout()

        # --- Entry Mode ---
        self.entry_mode_input = QComboBox()
        self.entry_mode_input.addItems(["Amount", "Miles"])
        form.addRow("Entry Mode:", self.entry_mode_input)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        form.addRow("Date:", self.date_input)
        
        self.amount_input = QLineEdit()            
        form.addRow("Amount:", self.amount_input)
        
        self.category_input = QComboBox()
        self.category_input.addItems(["Supplies", "Labor", "Transportation"])
        form.addRow("Category:", self.category_input)

        # Mileage row container
        self.mileage_input = QLineEdit()
        self.mileage_row = QWidget()
        mileage_layout = QHBoxLayout(self.mileage_row)
        mileage_layout.setContentsMargins(0, 0, 0, 0)
        mileage_layout.addWidget(self.mileage_input)
        form.addRow("Mileage:", self.mileage_row)
        mileage_label = form.labelForField(self.mileage_row)
        mileage_label.hide()
        self.mileage_row.hide()
        
        # Rate row container
        self.rate_input = QLineEdit()
        self.rate_input.setText("0.67")
        self.rate_row = QWidget()
        rate_layout = QHBoxLayout(self.rate_row)
        rate_layout.setContentsMargins(0, 0, 0, 0)
        rate_layout.addWidget(self.rate_input)
        form.addRow("Rate:", self.rate_row)
        rate_label = form.labelForField(self.rate_row)
        rate_label.hide()
        self.rate_row.hide()

        # I want comments to be last
        self.comment_input = QLineEdit()
        form.addRow("Comment:", self.comment_input)

        return form

    def build_buttons(self):

        # submit
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

        self.delete_button = QPushButton("Delete Expense")
        self.delete_button.setEnabled(False)

        self.delete_button.setStyleSheet(
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
            QPushButton:disabled {
                background-color: #aaaaaa;
                color: #eeeeee;
            }
            """
        )

        return self.submit_button, self.delete_button

    def build_table(self):
        self.table = QTableWidget()
        
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            """
            QTableWidget {
                background-color: white;
                alternate-background-color: #f5f5f5;
            }
            """
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setColumnCount(len(ExpenseColumns))
        self.table.setHorizontalHeaderLabels(
            ["Date", "Amount", "Comment", "Category", "Timestamp"]
        )

        # timestamp column hidden
        self.table.setColumnHidden(ExpenseColumns.TIMESTAMP, True)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        return self.table

    def assemble_layout(self):
        central = QWidget(self.parent)
        layout = QVBoxLayout(central)

        layout.addLayout(self.form_layout)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.table)
    
        self.parent.setCentralWidget(central)












