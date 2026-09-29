import csv
import sqlite3


DATABASE = "database/banking.db"


def load_daily_file(file_path):

    connection = sqlite3.connect(DATABASE)

    with open(file_path, "r", newline="") as file:

        reader = csv.DictReader(file)

        for row in reader:

            connection.execute("""
                INSERT INTO transactions
                (
                    transaction_id,
                    account_id,
                    transaction_date,
                    transaction_type,
                    amount,
                    currency
                )
                VALUES (?, ?, ?, ?, ?, ?)

                ON CONFLICT(transaction_id)
                DO UPDATE SET
                    account_id = excluded.account_id,
                    transaction_date = excluded.transaction_date,
                    transaction_type = excluded.transaction_type,
                    amount = excluded.amount,
                    currency = excluded.currency
            """, (
                row["transaction_id"],
                row["account_id"],
                row["transaction_date"],
                row["transaction_type"],
                row["amount"],
                row["currency"]
            ))

    connection.commit()
    connection.close()


if __name__ == "__main__":

    load_daily_file(
        "data/daily/transactions_20260909.csv"
    )

    print("Daily file loaded successfully.")