import os
import sys
import sqlite3

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from src.orchestration.database_source import DEFAULT_DB_PATH


def run_database_transformations(db_path=None):
    if db_path is None:
        import os
        db_path = os.environ.get("BANKING_DB_PATH", DEFAULT_DB_PATH)
    with sqlite3.connect(db_path) as connection:
        rows = connection.execute("""
            SELECT
                transaction_id,
                account_id,
                transaction_date,
                transaction_type,
                amount
            FROM transactions
        """).fetchall()

        columns = [
            "transaction_id",
            "account_id",
            "transaction_date",
            "transaction_type",
            "amount",
        ]

    if not rows:
        raise ValueError("No transactions found in the database.")

    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

    # Create Spark session
    spark = (
        SparkSession.builder
        .appName("BankingDatabaseTransformations")
        .master("local[*]")
        .getOrCreate()
    )

    try:
        # Convert database rows into a Spark DataFrame
        transactions_df = spark.createDataFrame(rows, columns)

        # Count CREDIT transactions
        credit_df = transactions_df.filter(
            F.col("transaction_type") == "CREDIT"
        )

        # Find high-value transactions
        high_value_df = transactions_df.filter(
            F.col("amount") > 3000
        )

        # Classify transactions
        classified_df = transactions_df.withColumn(
            "transaction_size",
            F.when(
                F.col("amount") >= 3000,
                "HIGH"
            ).otherwise("NORMAL")
        )

        print("\n--- Database Transactions ---")
        classified_df.show(10)

        return {
            "total_transactions": transactions_df.count(),
            "credit_transactions": credit_df.count(),
            "high_value_transactions": high_value_df.count(),
        }

    finally:
        spark.stop()


if __name__ == "__main__":
    result = run_database_transformations()
    print("\nDatabase transformation summary:", result)