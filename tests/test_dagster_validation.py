import sqlite3

import pytest

from src.orchestration.data_quality import validate_transactions


def create_test_database(db_path, transactions):
    with sqlite3.connect(db_path) as connection:
        connection.execute("""
            CREATE TABLE transactions (
                transaction_id TEXT,
                account_id TEXT,
                transaction_date TEXT,
                transaction_type TEXT,
                amount REAL
            )
        """)

        connection.executemany("""
            INSERT INTO transactions (
                transaction_id,
                account_id,
                transaction_date,
                transaction_type,
                amount
            )
            VALUES (?, ?, ?, ?, ?)
        """, transactions)


def test_valid_transactions_pass(tmp_path):
    db_path = tmp_path / "valid_banking.db"

    create_test_database(
        db_path,
        [("T001", "A1001", "2026-10-15", "CREDIT", 500)],
    )

    assert validate_transactions(db_path) is True


def test_invalid_transaction_fails(tmp_path):
    db_path = tmp_path / "invalid_banking.db"

    create_test_database(
        db_path,
        [("", "A1001", "2026-10-15", "CREDIT", 500)],
    )

    with pytest.raises(ValueError, match="invalid transactions found"):
        validate_transactions(db_path)


def test_empty_database_fails(tmp_path):
    db_path = tmp_path / "empty_banking.db"

    create_test_database(db_path, [])

    with pytest.raises(ValueError, match="No transactions found"):
        validate_transactions(db_path)