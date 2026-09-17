import sys
from datetime import date, datetime

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidgetItem,
    QMessageBox,
)

from data.expense_repository import ExpenseRepository
from data.expense_repository_db import ExpenseRepositoryDB
from models.expense import Expense
from src.enums import ExpenseColumns
from src.connections import connect_signals
from src.ui_setup import ExpenseUI

# Toggle which storage backend the app uses. Both expose the same
# load_all/add/update/delete_by_id interface, so nothing else needs to change.
USE_DATABASE = True


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.editing_row = -1
        self.expense_repo = ExpenseRepositoryDB() if USE_DATABASE else ExpenseRepository()
        self.expenses: dict[int, Expense] = {}

        self.setWindowTitle("test")
        self.setMinimumSize(500, 300)

        # build ui
        self.ui = ExpenseUI(self)
        self.ui.entry_mode_input.currentTextChanged.connect(self.toggle_entry_mode)

        # load from repository (db or csv, depending on USE_DATABASE)
        self.load_expenses()

        connect_signals(self)


    # ---------------------------------------------------------
    # LOAD ROW INTO FORM
    # ---------------------------------------------------------
    def on_row_select(self):
        self.ui.delete_button.setEnabled(True)
        selected = self.ui.table.currentRow()
        if selected < 0:
            return

        self.editing_row = selected
        expense_id = int(self.ui.table.item(selected, ExpenseColumns.ID).text())
        expense = self.expenses.get(expense_id)
        if expense is None:
            return

        # load date
        self.ui.date_input.setDate(QDate.fromString(expense.date, "yyyy-MM-dd"))

        # load comment
        self.ui.comment_input.setText(expense.comment)

        # setting this triggers toggle_entry_mode, which shows the right fields
        # (and, for Miles, forces category to Transportation)
        self.ui.entry_mode_input.setCurrentText(expense.entry_mode)

        # load category AFTER entry_mode, so the saved value overrides the
        # auto-default toggle_entry_mode just applied
        self.ui.category_input.setCurrentText(expense.category)

        if expense.entry_mode == "Miles":
            self.ui.mileage_input.setText(str(expense.mileage))
            self.ui.rate_input.setText(str(expense.rate))
        else:
            self.ui.amount_input.setText(f"{expense.amount:g}")

        self.ui.submit_button.setText("Save Changes")

    # ---------------------------------------------------------
    # SAVE CHANGES (FORM → TABLE → REPO)
    # ---------------------------------------------------------
    def save_changes_to_expense(self):
        row = self.editing_row
        if row < 0:
            return

        # validate form
        is_valid, error_message = self.validate_inputs()
        if not is_valid:
            self.show_error(error_message)
            return

        # id identifies the row
        expense_id = int(self.ui.table.item(row, ExpenseColumns.ID).text())

        # created_at should never change on edit — reuse the original value
        existing = self.expenses.get(expense_id)
        created_at = existing.timestamp if existing else datetime.now().isoformat(timespec="seconds")

        updated = self.build_expense_from_form(expense_id=expense_id, created_at=created_at)

        # prevent selection reload during save
        self.ui.table.blockSignals(True)
        self.ui.table.setSortingEnabled(False)

        # update table row
        self.ui.table.setItem(row, ExpenseColumns.DATE, QTableWidgetItem(updated.date))
        self.ui.table.setItem(
            row,
            ExpenseColumns.AMOUNT,
            QTableWidgetItem(f"${updated.amount:,.2f}")
        )
        self.ui.table.setItem(row, ExpenseColumns.COMMENT, QTableWidgetItem(updated.comment))
        self.ui.table.setItem(row, ExpenseColumns.CATEGORY, QTableWidgetItem(updated.category))

        # update repository
        self.expense_repo.update(updated)
        self.expenses[expense_id] = updated

        # re-enable sorting
        self.ui.table.setSortingEnabled(True)
        self.sort_table_by_id()

        self.ui.table.blockSignals(False)

        # reset form
        self.ui.submit_button.setText("Add Expense")
        self.editing_row = -1
        self.clear_form()

    # ---------------------------------------------------------
    # ADD NEW EXPENSE
    # ---------------------------------------------------------
    def on_submit_button_push(self):
        if self.ui.submit_button.text() == "Add Expense":
            self.add_new_expense()
        else:
            self.save_changes_to_expense()

    def add_new_expense(self):
        is_valid, error_message = self.validate_inputs()
        if not is_valid:
            self.show_error(error_message)
            return

        created_at = datetime.now().isoformat(timespec="seconds")
        expense = self.build_expense_from_form(expense_id=None, created_at=created_at)

        # repo assigns the id on insert — we don't know it beforehand
        new_id = self.expense_repo.add(expense)
        expense.id = new_id

        self.expenses[new_id] = expense
        self.add_expense_to_ui_table(expense)
        self.sort_table_by_id()
        self.clear_form()

    def build_expense_from_form(self, expense_id: int | None, created_at: str) -> Expense:
        """Reads the form and produces an Expense, handling both modes."""
        date_str = self.ui.date_input.date().toString("yyyy-MM-dd")
        comment = self.ui.comment_input.text()
        category = self.ui.category_input.currentText()
        mode = self.ui.entry_mode_input.currentText()

        if mode == "Miles":
            mileage = float(self.ui.mileage_input.text())
            rate = float(self.ui.rate_input.text())
            amount_value = round(mileage * rate, 2)
            return Expense(
                date_str, amount_value, comment, category, created_at,
                id=expense_id, entry_mode="Miles", mileage=mileage, rate=rate
            )
        else:
            amount_value = float(self.ui.amount_input.text())
            return Expense(
                date_str, amount_value, comment, category, created_at,
                id=expense_id, entry_mode="Amount", mileage=None, rate=None
            )

    # ---------------------------------------------------------
    # DELETE EXPENSE
    # ---------------------------------------------------------
    def on_delete_button_push(self):
        row = self.ui.table.currentRow()
        if row < 0:
            return

        expense_id = int(self.ui.table.item(row, ExpenseColumns.ID).text())

        # delete from repository
        self.expense_repo.delete_by_id(expense_id)
        self.expenses.pop(expense_id, None)
        # remove from table
        self.ui.table.removeRow(row)

        # Reset form
        self.clear_form()
        self.ui.submit_button.setText("Add Expense")
        self.editing_row = -1

    def toggle_entry_mode(self):
        is_miles = self.ui.entry_mode_input.currentText() == "Miles"
        form = self.ui.form_layout

        self.ui.amount_input.setVisible(not is_miles)
        form.labelForField(self.ui.amount_input).setVisible(not is_miles)

        self.ui.mileage_row.setVisible(is_miles)
        form.labelForField(self.ui.mileage_row).setVisible(is_miles)

        self.ui.rate_row.setVisible(is_miles)
        form.labelForField(self.ui.rate_row).setVisible(is_miles)

        if is_miles:
            self.ui.category_input.setCurrentText("Transportation")
        else:
            self.ui.category_input.setCurrentText("Supplies")

        self.ui.category_input.setEnabled(not is_miles)

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------
    def validate_inputs(self):
        comment_text = self.ui.comment_input.text().strip()
        selected_date = self.ui.date_input.date().toPyDate()
        mode = self.ui.entry_mode_input.currentText()

        if selected_date > date.today():
            return False, "Date cannot be in the future."

        if not comment_text:
            return False, "Comment cannot be empty."

        if mode == "Miles":
            try:
                mileage = float(self.ui.mileage_input.text())
                rate = float(self.ui.rate_input.text())
            except ValueError:
                return False, "Mileage and rate must be numbers."

            if mileage <= 0:
                return False, "Mileage must be greater than zero."

            if rate <= 0:
                return False, "Rate must be greater than zero."
        else:
            try:
                amount_value = float(self.ui.amount_input.text())
            except ValueError:
                return False, "Amount must be a number."

            if amount_value <= 0:
                return False, "Amount must be greater than zero."

        return True, ""

    def show_error(self, message: str):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("Invalid Input")
        box.setText(message)
        box.exec()

    # ---------------------------------------------------------
    # TABLE HELPERS
    # ---------------------------------------------------------
    def add_expense_to_ui_table(self, expense: Expense):
        self.ui.table.setSortingEnabled(False)

        row = self.ui.table.rowCount()
        self.ui.table.insertRow(row)

        self.ui.table.setItem(row, ExpenseColumns.DATE, QTableWidgetItem(expense.date))
        self.ui.table.setItem(
            row,
            ExpenseColumns.AMOUNT,
            QTableWidgetItem(f"${expense.amount:,.2f}")
        )
        self.ui.table.setItem(row, ExpenseColumns.COMMENT, QTableWidgetItem(expense.comment))
        self.ui.table.setItem(row, ExpenseColumns.CATEGORY, QTableWidgetItem(expense.category))

        # store the id as numeric data (not just text) so the table sorts it
        # as a number, not alphabetically ("10" would otherwise sort before "2")
        id_item = QTableWidgetItem()
        id_item.setData(Qt.ItemDataRole.DisplayRole, expense.id)
        self.ui.table.setItem(row, ExpenseColumns.ID, id_item)

        self.ui.table.setSortingEnabled(True)

    def sort_table_by_id(self):
        # ids increment as expenses are added, so sorting by id descending
        # shows newest first
        self.ui.table.sortItems(ExpenseColumns.ID, Qt.SortOrder.DescendingOrder)

    def clear_form(self):
        self.ui.date_input.setDate(QDate.currentDate())
        self.ui.amount_input.clear()
        self.ui.comment_input.clear()
        self.ui.category_input.setCurrentIndex(0)
        self.ui.delete_button.setEnabled(False)

    # ---------------------------------------------------------
    # LOAD FROM REPOSITORY
    # ---------------------------------------------------------
    def load_expenses(self):
        rows = self.expense_repo.load_all()
        for expense in rows:
            self.expenses[expense.id] = expense
            self.add_expense_to_ui_table(expense)
        self.sort_table_by_id()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()