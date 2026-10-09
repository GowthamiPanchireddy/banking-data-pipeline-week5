import os
import sys
from pyspark.sql import SparkSession


# Use the same Python interpreter for Spark
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


# Create Spark session
spark = (
    SparkSession.builder
    .appName("BankingDataLoad")
    .master("local[*]")
    .getOrCreate()
)


# Project root
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)


# File paths
ACCOUNTS_FILE = os.path.join(
    PROJECT_ROOT, "data", "reference", "accounts.csv"
)

CUSTOMERS_FILE = os.path.join(
    PROJECT_ROOT, "data", "reference", "customers.csv"
)

BRANCHES_FILE = os.path.join(
    PROJECT_ROOT, "data", "reference", "branches.csv"
)

TRANSACTIONS_FILE = os.path.join(
    PROJECT_ROOT, "data", "generated", "transactions_100k.csv"
)


# Load CSV files into Spark DataFrames
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

transactions_df = spark.read.csv(
    TRANSACTIONS_FILE,
    header=True,
    inferSchema=True
)


# Inspect sample rows
print("\n--- Accounts ---")
accounts_df.show(5)

print("\n--- Customers ---")
customers_df.show(5)

print("\n--- Branches ---")
branches_df.show(5)

print("\n--- Transactions ---")
transactions_df.show(5)


# Inspect schemas
print("\n--- Accounts Schema ---")
accounts_df.printSchema()

print("\n--- Customers Schema ---")
customers_df.printSchema()

print("\n--- Branches Schema ---")
branches_df.printSchema()

print("\n--- Transactions Schema ---")
transactions_df.printSchema()


# Inspect row counts
print("\n--- Row Counts ---")
print("Accounts:", accounts_df.count())
print("Customers:", customers_df.count())
print("Branches:", branches_df.count())
print("Transactions:", transactions_df.count())


# Stop Spark
spark.stop()