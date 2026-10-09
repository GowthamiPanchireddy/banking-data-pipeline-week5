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
    .appName("BankingDataQuality")
    .master("local[*]")
    .getOrCreate()
)


# Project root
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)


# File paths
TRANSACTIONS_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "generated",
    "transactions_100k.csv"
)

ACCOUNTS_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "reference",
    "accounts.csv"
)

CUSTOMERS_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "reference",
    "customers.csv"
)

BRANCHES_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "reference",
    "branches.csv"
)


# Load DataFrames
transactions_df = spark.read.csv(
    TRANSACTIONS_FILE,
    header=True,
    inferSchema=True
)

accounts_df = spark.read.csv(
    ACCOUNTS_FILE,
    header=True,
    inferSchema=True
)

customers_df = spark.read.csv(
    CUSTOMERS_FILE,
    header=True,
    inferSchema=True
)

branches_df = spark.read.csv(
    BRANCHES_FILE,
    header=True,
    inferSchema=True
)


print("\n--- Data Quality Checks ---")


# 1. Null transaction IDs
null_transaction_id_count = transactions_df.filter(
    F.col("transaction_id").isNull()
).count()

print(
    "Null transaction IDs:",
    null_transaction_id_count
)


# 2. Null account IDs
null_account_id_count = transactions_df.filter(
    F.col("account_id").isNull()
).count()

print(
    "Null account IDs:",
    null_account_id_count
)


# 3. Null amounts
null_amount_count = transactions_df.filter(
    F.col("amount").isNull()
).count()

print(
    "Null amounts:",
    null_amount_count
)


# 4. Duplicate transaction IDs
duplicate_transaction_id_count = (
    transactions_df
    .groupBy("transaction_id")
    .count()
    .filter(F.col("count") > 1)
    .count()
)

print(
    "Duplicate transaction IDs:",
    duplicate_transaction_id_count
)


# 5. Transactions referencing nonexistent accounts
invalid_account_count = (
    transactions_df
    .join(
        accounts_df.select("account_id"),
        "account_id",
        "left_anti"
    )
    .count()
)

print(
    "Transactions with invalid account IDs:",
    invalid_account_count
)


# 6. Accounts referencing nonexistent customers
invalid_customer_count = (
    accounts_df
    .join(
        customers_df.select("customer_id"),
        "customer_id",
        "left_anti"
    )
    .count()
)

print(
    "Accounts with invalid customer IDs:",
    invalid_customer_count
)


# 7. Accounts referencing nonexistent branches
invalid_branch_count = (
    accounts_df
    .join(
        branches_df.select("branch_id"),
        "branch_id",
        "left_anti"
    )
    .count()
)

print(
    "Accounts with invalid branch IDs:",
    invalid_branch_count
)


# Overall result
total_errors = (
    null_transaction_id_count
    + null_account_id_count
    + null_amount_count
    + duplicate_transaction_id_count
    + invalid_account_count
    + invalid_customer_count
    + invalid_branch_count
)


if total_errors == 0:
    print("\nData Quality Result: PASS")
else:
    print("\nData Quality Result: FAIL")

print("Total DQ errors:", total_errors)


# Stop Spark
spark.stop()