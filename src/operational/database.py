import sqlite3
import csv
from pathlib import Path


DB_PATH = Path("database/banking.db")


def get_connection():
    connection = sqlite3.connect(DB_PATH)

    # Enable foreign key enforcement
    connection.execute("PRAGMA foreign_keys = ON")

    return connection

def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer (
            customer_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            customer_segment TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS branch (
            branch_id TEXT PRIMARY KEY,
            branch_name TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS account (
            account_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            branch_id TEXT NOT NULL,
            account_type TEXT NOT NULL,
            account_status TEXT NOT NULL,
            FOREIGN KEY (customer_id)
                REFERENCES customer(customer_id),
            FOREIGN KEY (branch_id)
                REFERENCES branch(branch_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            transaction_date TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL CHECK (amount > 0),
            currency TEXT NOT NULL,
            FOREIGN KEY (account_id)
                REFERENCES account(account_id)
        )
    """)

    connection.commit()
    connection.close()




def load_csv_data():
    connection = get_connection()
    cursor = connection.cursor()

    input_folder = Path("data/reference")

    try:
        # 1. Load customers
        with open(input_folder / "customers.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                cursor.execute("""
                    INSERT OR IGNORE INTO customer
                    (customer_id, customer_name, email, customer_segment)
                    VALUES (?, ?, ?, ?)
                """, (
                    row["customer_id"],
                    row["customer_name"],
                    row["email"],
                    row["customer_segment"]
                ))

        # 2. Load branches
        with open(input_folder / "branches.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                cursor.execute("""
                    INSERT OR IGNORE INTO branch
                    (branch_id, branch_name, city, state)
                    VALUES (?, ?, ?, ?)
                """, (
                    row["branch_id"],
                    row["branch_name"],
                    row["city"],
                    row["state"]
                ))

        # 3. Load accounts
        with open(input_folder / "accounts.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                cursor.execute("""
                    INSERT OR IGNORE INTO account
                    (account_id, customer_id, branch_id, account_type, account_status)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    row["account_id"],
                    row["customer_id"],
                    row["branch_id"],
                    row["account_type"],
                    row["account_status"]
                ))

        # 4. Load valid transactions
        with open(Path("data/validated") / "valid_transactions.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                cursor.execute("""
                    INSERT OR IGNORE INTO transactions
                    (transaction_id, account_id, transaction_date,
                     transaction_type, amount, currency)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    row["transaction_id"],
                    row["account_id"],
                    row["transaction_date"],
                    row["transaction_type"],
                    row["amount"],
                    row["currency"]
                ))

        connection.commit()

        print("CSV data loaded successfully!")

    except sqlite3.IntegrityError as error:
        connection.rollback()
        print(f"Database integrity error: {error}")
        raise

    finally:
        connection.close()

if __name__ == "__main__":
    create_tables()
    load_csv_data()
    print("Database and tables created successfully!")