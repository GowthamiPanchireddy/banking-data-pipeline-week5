import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def run_transformations():
    # Use the same Python interpreter for Spark
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

    # Create Spark session
    spark = (
        SparkSession.builder
        .appName("BankingTransformations")
        .master("local[*]")
        .getOrCreate()
    )

    try:
        # Project root
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../..")
        )

        # Transactions file
        transactions_file = os.path.join(
            project_root,
            "data",
            "generated",
            "transactions_100k.csv"
        )

        # Load transactions
        transactions_df = spark.read.csv(
            transactions_file,
            header=True,
            inferSchema=True
        )

        # Select required columns
        selected_df = transactions_df.select(
            "transaction_id",
            "account_id",
            "transaction_date",
            "transaction_type",
            "amount"
        )

        print("\n--- Selected Columns ---")
        selected_df.show(5)

        # Filter CREDIT transactions
        credit_df = transactions_df.filter(
            F.col("transaction_type") == "CREDIT"
        )

        print("\n--- CREDIT Transactions ---")
        credit_df.show(5)
        print("CREDIT count:", credit_df.count())

        # Filter high-value transactions
        high_value_threshold = 3000

        high_value_df = transactions_df.filter(
            F.col("amount") > high_value_threshold
        )

        print("\n--- High-Value Transactions ---")
        high_value_df.show(5)
        print("High-value count:", high_value_df.count())

        # Create transaction_size column
        classified_df = transactions_df.withColumn(
            "transaction_size",
            F.when(
                F.col("amount") >= high_value_threshold,
                "HIGH"
            ).otherwise("NORMAL")
        )

        print("\n--- Derived Column ---")
        classified_df.select(
            "transaction_id",
            "amount",
            "transaction_size"
        ).show(10)

        # Return useful summary information
        return {
            "total_transactions": transactions_df.count(),
            "credit_transactions": credit_df.count(),
            "high_value_transactions": high_value_df.count()
        }

    finally:
        # Stop Spark even if an error occurs
        spark.stop()


if __name__ == "__main__":
    result = run_transformations()
    print("\nTransformation summary:", result)