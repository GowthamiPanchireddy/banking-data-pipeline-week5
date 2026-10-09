import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


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


# Project root
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)


# Transactions file
TRANSACTIONS_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "generated",
    "transactions_100k.csv"
)


# Load transactions
transactions_df = spark.read.csv(
    TRANSACTIONS_FILE,
    header=True,
    inferSchema=True
)


# 1. Select required columns
selected_df = transactions_df.select(
    "transaction_id",
    "account_id",
    "transaction_date",
    "transaction_type",
    "amount"
)

print("\n--- Selected Columns ---")
selected_df.show(5)


# 2. Filter CREDIT transactions
credit_df = transactions_df.filter(
    transactions_df.transaction_type == "CREDIT"
)

print("\n--- CREDIT Transactions ---")
credit_df.show(5)

print("CREDIT count:", credit_df.count())


# 3. Filter high-value transactions
HIGH_VALUE_THRESHOLD = 3000

high_value_df = transactions_df.filter(
    transactions_df.amount > HIGH_VALUE_THRESHOLD
)

print("\n--- High-Value Transactions ---")
high_value_df.show(5)

print(
    "High-value count:",
    high_value_df.count()
)


# 4. Create a derived column using withColumn
classified_df = transactions_df.withColumn(
    "transaction_size",
    F.when(
        transactions_df.amount >= HIGH_VALUE_THRESHOLD,
        "HIGH"
    ).otherwise("NORMAL")
)

print("\n--- Derived Column ---")
classified_df.select(
    "transaction_id",
    "amount",
    "transaction_size"
).show(10)


# Stop Spark
spark.stop()