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
    .appName("BankingAnalytics")
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

branches_df = spark.read.csv(
    BRANCHES_FILE,
    header=True,
    inferSchema=True
)


# 1. Summary by transaction type
transaction_type_summary = transactions_df.groupBy(
    "transaction_type"
).agg(
    F.count("*").alias("transaction_count"),
    F.sum("amount").alias("total_amount"),
    F.avg("amount").alias("average_amount")
)

print("\n--- Summary by Transaction Type ---")
transaction_type_summary.show()


# 2. Summary by account
account_summary = transactions_df.groupBy(
    "account_id"
).agg(
    F.count("*").alias("transaction_count"),
    F.sum("amount").alias("total_amount"),
    F.avg("amount").alias("average_amount")
)

print("\n--- Summary by Account ---")
account_summary.show(10)


# 3. Join transactions with accounts
transaction_account_df = transactions_df.join(
    accounts_df,
    transactions_df.account_id == accounts_df.account_id,
    "inner"
)

print("\n--- Transactions + Accounts ---")
transaction_account_df.select(
    transactions_df.transaction_id,
    transactions_df.account_id,
    accounts_df.customer_id,
    accounts_df.branch_id,
    transactions_df.transaction_type,
    transactions_df.amount
).show(10)


# 4. Summary by branch
branch_summary = transaction_account_df.groupBy(
    "branch_id"
).agg(
    F.count("*").alias("transaction_count"),
    F.sum("amount").alias("total_amount"),
    F.avg("amount").alias("average_amount")
)

print("\n--- Summary by Branch ---")
branch_summary.show()


# 5. Add branch names
branch_analysis = branch_summary.join(
    branches_df,
    branch_summary.branch_id == branches_df.branch_id,
    "inner"
)

print("\n--- Branch Analysis ---")
branch_analysis.select(
    branch_summary.branch_id,
    branches_df.branch_name,
    branches_df.city,
    branch_summary.transaction_count,
    branch_summary.total_amount,
    branch_summary.average_amount
).show()


# Stop Spark
spark.stop()