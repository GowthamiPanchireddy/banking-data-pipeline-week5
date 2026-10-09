import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

spark = (
    SparkSession.builder
    .appName("BankingExecutionConcepts")
    .master("local[*]")
    .getOrCreate()
)

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

TRANSACTIONS_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "generated",
    "transactions_100k.csv"
)

transactions_df = spark.read.csv(
    TRANSACTIONS_FILE,
    header=True,
    inferSchema=True
)

# Partitions
print("\n--- Partitions ---")
print("Number of partitions:", transactions_df.rdd.getNumPartitions())

# Transformation
credit_df = transactions_df.filter(
    F.col("transaction_type") == "CREDIT"
)

print("\n--- Transformation ---")
print("filter() is a transformation.")
print("It creates a new DataFrame but does not execute immediately.")

# Action
credit_count = credit_df.count()

print("\n--- Action ---")
print("count() is an action.")
print("CREDIT transaction count:", credit_count)

# Shuffle operation
branch_summary = transactions_df.groupBy(
    "transaction_type"
).agg(
    F.count("*").alias("transaction_count"),
    F.sum("amount").alias("total_amount")
)

print("\n--- Shuffle ---")
print("groupBy() may cause a shuffle because data may need to move between partitions.")

print("\n--- GroupBy Result ---")
branch_summary.show()

spark.stop()