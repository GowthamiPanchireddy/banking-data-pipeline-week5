import sqlite3


OPERATIONAL_DB = "database/banking.db"
ANALYTICS_DB = "database/analytics.db"


def build_analytics():

    source = sqlite3.connect(OPERATIONAL_DB)
    target = sqlite3.connect(ANALYTICS_DB)

    # Load customers
    customers = source.execute("""
        SELECT customer_id, customer_name
        FROM customer
    """).fetchall()

    target.executemany("""
        INSERT OR REPLACE INTO dim_customer
        (customer_id, customer_name)
        VALUES (?, ?)
    """, customers)

    # Load accounts
    accounts = source.execute("""
        SELECT account_id, customer_id, account_type
        FROM account
    """).fetchall()

    target.executemany("""
        INSERT OR REPLACE INTO dim_account
        (account_id, customer_id, account_type)
        VALUES (?, ?, ?)
    """, accounts)

    # Load branches
    branches = source.execute("""
        SELECT branch_id, branch_name
        FROM branch
    """).fetchall()

    target.executemany("""
        INSERT OR REPLACE INTO dim_branch
        (branch_id, branch_name)
        VALUES (?, ?)
    """, branches)

    # Load dates
    dates = source.execute("""
        SELECT DISTINCT transaction_date
        FROM transactions
    """).fetchall()

    target.executemany("""
        INSERT OR REPLACE INTO dim_date
        (date_key)
        VALUES (?)
    """, dates)

    # Load transactions into fact table
    transactions = source.execute("""
        SELECT
            t.transaction_id,
            t.account_id,
            a.branch_id,
            t.transaction_date,
            t.transaction_type,
            t.amount,
            t.currency
        FROM transactions t
        LEFT JOIN account a
            ON t.account_id = a.account_id
    """).fetchall()

    target.executemany("""
        INSERT OR REPLACE INTO fact_transaction
        (
            transaction_id,
            account_id,
            branch_id,
            date_key,
            transaction_type,
            amount,
            currency
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, transactions)

    target.commit()

    source.close()
    target.close()

    print("Analytics data loaded successfully.")


if __name__ == "__main__":
    build_analytics()