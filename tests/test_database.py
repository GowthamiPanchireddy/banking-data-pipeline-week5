import sqlite3
import pytest

from src.operational.database import get_connection, create_tables, load_csv_data


def test_expected_tables():
    create_tables()

    connection = get_connection()

    tables = connection.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
    """).fetchall()

    table_names = {row[0] for row in tables}

    assert "customer" in table_names
    assert "branch" in table_names
    assert "account" in table_names
    assert "transactions" in table_names

    connection.close()


def test_foreign_keys_enabled():
    connection = get_connection()

    foreign_keys = connection.execute(
        "PRAGMA foreign_keys"
    ).fetchone()[0]

    assert foreign_keys == 1

    connection.close()


def test_expected_row_counts():
    connection = get_connection()

    assert connection.execute(
        "SELECT COUNT(*) FROM customer"
    ).fetchone()[0] == 6

    assert connection.execute(
        "SELECT COUNT(*) FROM branch"
    ).fetchone()[0] == 3

    assert connection.execute(
        "SELECT COUNT(*) FROM account"
    ).fetchone()[0] == 10

    assert connection.execute(
        "SELECT COUNT(*) FROM transactions"
    ).fetchone()[0] == 20

    connection.close()


def test_duplicate_primary_key_rejected():
    connection = get_connection()

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("""
            INSERT INTO customer
            (customer_id, customer_name, email, customer_segment)
            VALUES ('C1001', 'Duplicate Customer',
                    'duplicate@example.com', 'RETAIL')
        """)

    connection.rollback()
    connection.close()


def test_invalid_foreign_key_rejected():
    connection = get_connection()

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("""
            INSERT INTO transactions
            (transaction_id, account_id, transaction_date,
             transaction_type, amount, currency)
            VALUES ('TEST_FK', 'A9999', '2026-09-06',
                    'DEBIT', 50, 'USD')
        """)

    connection.rollback()
    connection.close()


def test_invalid_amount_rejected():
    connection = get_connection()

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute("""
            INSERT INTO transactions
            (transaction_id, account_id, transaction_date,
             transaction_type, amount, currency)
            VALUES ('TEST_AMOUNT', 'A1001', '2026-09-06',
                    'DEBIT', -50, 'USD')
        """)

    connection.rollback()
    connection.close()


def test_rerun_does_not_create_duplicates():
    connection = get_connection()

    before = connection.execute(
        "SELECT COUNT(*) FROM transactions"
    ).fetchone()[0]

    connection.close()

    load_csv_data()

    connection = get_connection()

    after = connection.execute(
        "SELECT COUNT(*) FROM transactions"
    ).fetchone()[0]

    assert before == after

    connection.close()