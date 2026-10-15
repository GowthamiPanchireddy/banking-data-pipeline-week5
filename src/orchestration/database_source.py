import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "database" / "banking.db"
DB_PATH = Path(os.environ.get("BANKING_DB_PATH", DEFAULT_DB_PATH))


def get_transaction_count(db_path=DB_PATH):
    with sqlite3.connect(db_path) as connection:
        result = connection.execute(
            "SELECT COUNT(*) FROM transactions"
        ).fetchone()

    return result[0]


if __name__ == "__main__":
    count = get_transaction_count()
    print("Total transactions:", count)