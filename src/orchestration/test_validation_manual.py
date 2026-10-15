import sqlite3
from pathlib import Path

from src.orchestration.data_quality import validate_transactions


# Create a separate test database
test_db = Path("database") / "test_banking.db"
test_db.parent.mkdir(parents=True, exist_ok=True)

# Create the transactions table and insert invalid test data
with sqlite3.connect(test_db) as connection:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT,
            account_id TEXT,
            transaction_date TEXT,
            transaction_type TEXT,
            amount REAL
        )
    """)

    connection.execute("DELETE FROM transactions")

    connection.execute("""
        INSERT INTO transactions
        VALUES ('', 'A1001', '2026-09-06', 'CREDIT', 500)
    """)

print("Test database created with an invalid transaction.")

# Check whether validation correctly rejects invalid data
try:
    validate_transactions(test_db)
except ValueError as error:
    print(error)