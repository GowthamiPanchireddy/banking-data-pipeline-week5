import sqlite3


DATABASE = "database/analytics.db"


def test_fact_transaction_count():
    connection = sqlite3.connect(DATABASE)

    count = connection.execute(
        "SELECT COUNT(*) FROM fact_transaction"
    ).fetchone()[0]

    connection.close()

    assert count == 20


def test_fact_transaction_unique_ids():
    connection = sqlite3.connect(DATABASE)

    total = connection.execute(
        "SELECT COUNT(*) FROM fact_transaction"
    ).fetchone()[0]

    unique_ids = connection.execute(
        "SELECT COUNT(DISTINCT transaction_id) FROM fact_transaction"
    ).fetchone()[0]

    connection.close()

    assert total == unique_ids


def test_known_correction():
    connection = sqlite3.connect(DATABASE)

    amount = connection.execute("""
        SELECT amount
        FROM fact_transaction
        WHERE transaction_id = 'T1001'
    """).fetchone()[0]

    connection.close()

    assert amount == 550.0


def test_known_analytical_result():
    connection = sqlite3.connect(DATABASE)

    result = connection.execute("""
        SELECT COUNT(*), SUM(amount)
        FROM fact_transaction
        WHERE transaction_type = 'CREDIT'
    """).fetchone()

    connection.close()

    assert result[0] == 11
    assert result[1] == 4060.0