import pytest

from data.expense_repository_db import ExpenseRepositoryDB
from models.expense import Expense

@pytest.fixture
def repo():
    """A fresh ExpenseRepositoryDB backed by a throwaway test database file."""
    repository = ExpenseRepositoryDB(path="test_expense.db")
    yield repository
    repository.conn.close()
    if repository.path.exists():
        repository.path.unlink()

        import pytest

from data.expense_repository_db import ExpenseRepositoryDB
from models.expense import Expense


@pytest.fixture
def repo():
    """A fresh ExpenseRepositoryDB backed by a throwaway test database file."""
    repository = ExpenseRepositoryDB(path="test_expense.db")
    yield repository
    repository.conn.close()
    if repository.path.exists():
        repository.path.unlink()

def make_expense(**overrides):
    defaults = dict(
        date="2026-09-15",
        amount=42.50,
        comment="test expense",
        category="Supplies",
        timestamp="2026-09-15T10:00:00",
    )
    defaults.update(overrides)
    return Expense(**defaults)

# load all ----

def test_load_all_returns_empty_list_when_no_expenses(repo):
    assert repo.load_all() == []


def test_load_all_returns_all_inserted_expenses(repo):
    repo.add(make_expense(comment="first"))
    repo.add(make_expense(comment="second"))

    all_expenses = repo.load_all()

    assert len(all_expenses) == 2
    comments = {e.comment for e in all_expenses}
    assert comments == {"first", "second"}


def test_load_all_reconstructs_amount_mode_fields(repo):
    repo.add(make_expense(
        entry_mode="Amount", amount=25.00, mileage=None, rate=None
    ))

    loaded = repo.load_all()[0]

    assert loaded.entry_mode == "Amount"
    assert loaded.amount == 25.00
    assert loaded.mileage is None
    assert loaded.rate is None


def test_load_all_reconstructs_miles_mode_fields(repo):
    repo.add(make_expense(
        entry_mode="Miles", mileage=120.0, rate=0.67, category="Transportation"
    ))

    loaded = repo.load_all()[0]

    assert loaded.entry_mode == "Miles"
    assert loaded.mileage == 120.0
    assert loaded.rate == 0.67


def test_load_all_assigns_correct_id_to_each_expense(repo):
    id1 = repo.add(make_expense(comment="a"))
    id2 = repo.add(make_expense(comment="b"))

    all_expenses = {e.comment: e.id for e in repo.load_all()}

    assert all_expenses["a"] == id1
    assert all_expenses["b"] == id2


# add ----

def test_add_returns_an_id(repo):
    new_id = repo.add(make_expense())
    assert isinstance(new_id, int)


def test_add_persists_all_fields_correctly(repo):
    expense = make_expense(
        entry_mode="Miles", mileage=100.0, rate=0.67, category="Transportation"
    )
    new_id = repo.add(expense)

    row = repo.conn.execute(
        "SELECT * FROM expenses WHERE id = ?", (new_id,)
    ).fetchone()

    # column order: id, date, amount, comment, category, timestamp, entry_mode, mileage, rate
    assert row[1] == expense.date
    assert row[2] == expense.amount
    assert row[3] == expense.comment
    assert row[4] == expense.category
    assert row[5] == expense.timestamp
    assert row[6] == expense.entry_mode
    assert row[7] == expense.mileage
    assert row[8] == expense.rate


def test_add_assigns_unique_incrementing_ids(repo):
    id1 = repo.add(make_expense())
    id2 = repo.add(make_expense())
    assert id2 == id1 + 1


def test_add_amount_mode_stores_null_mileage_and_rate(repo):
    new_id = repo.add(make_expense(entry_mode="Amount", mileage=None, rate=None))

    mileage, rate = repo.conn.execute(
        "SELECT mileage, rate FROM expenses WHERE id = ?", (new_id,)
    ).fetchone()

    assert mileage is None
    assert rate is None


# update ----

def test_update_changes_only_the_target_row(repo):
    id1 = repo.add(make_expense(comment="unchanged"))
    id2 = repo.add(make_expense(comment="original"))

    updated_expense = make_expense(comment="edited", id=id2, timestamp="2026-09-15T10:00:00")
    repo.update(updated_expense)

    all_expenses = {e.id: e for e in repo.load_all()}
    assert all_expenses[id1].comment == "unchanged"
    assert all_expenses[id2].comment == "edited"


def test_update_does_not_change_timestamp(repo):
    original = make_expense(timestamp="2026-01-01T09:00:00")
    new_id = repo.add(original)

    updated_expense = make_expense(comment="edited", id=new_id, timestamp="2099-01-01T00:00:00")
    repo.update(updated_expense)

    loaded = repo.load_all()[0]
    assert loaded.timestamp == "2026-01-01T09:00:00"  # unchanged, despite what we passed in


def test_update_with_nonexistent_id_affects_nothing(repo):
    repo.add(make_expense(comment="only expense"))

    fake_update = make_expense(comment="should not appear", id=9999)
    repo.update(fake_update)

    all_expenses = repo.load_all()
    assert len(all_expenses) == 1
    assert all_expenses[0].comment == "only expense"


def test_update_preserves_entry_mode_fields(repo):
    original = make_expense(entry_mode="Amount", mileage=None, rate=None)
    new_id = repo.add(original)

    switched = make_expense(
        comment="switched to miles",
        id=new_id,
        entry_mode="Miles",
        mileage=50.0,
        rate=0.70,
        category="Transportation",
    )
    repo.update(switched)

    loaded = repo.load_all()[0]
    assert loaded.entry_mode == "Miles"
    assert loaded.mileage == 50.0
    assert loaded.rate == 0.70   