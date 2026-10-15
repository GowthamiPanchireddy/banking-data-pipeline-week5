import sqlite3

from src.orchestration.database_source import DB_PATH


def validate_transactions(db_path=None):
    if db_path is None:
        import os
        db_path = os.environ.get("BANKING_DB_PATH", DB_PATH)
    with sqlite3.connect(db_path) as connection:
        result = connection.execute("""
            SELECT
                COUNT(*) AS total_rows,
                SUM(
                    CASE
                        WHEN transaction_id IS NULL
                             OR TRIM(transaction_id) = ''
                             OR account_id IS NULL
                             OR TRIM(account_id) = ''
                             OR transaction_date IS NULL
                             OR transaction_type IS NULL
                             OR amount IS NULL
                             OR amount < 0
                        THEN 1
                        ELSE 0
                    END
                ) AS invalid_rows
            FROM transactions
        """).fetchone()

    total_rows = result[0]
    invalid_rows = result[1] or 0

    if total_rows == 0:
        raise ValueError("Validation failed: No transactions found.")

    if invalid_rows > 0:
        raise ValueError(
            f"Validation failed: {invalid_rows} invalid transactions found."
        )

    print(f"Validation passed: {total_rows} transactions checked.")
    return True


if __name__ == "__main__":
    validate_transactions()