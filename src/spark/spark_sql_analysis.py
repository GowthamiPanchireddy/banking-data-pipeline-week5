import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

spark = (
    SparkSession.builder
    .appName("BankingSparkSQL")
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

# DataFrame API analysis
dataframe_summary = transactions_df.groupBy(
    "transaction_type"
).agg(
    F.count("*").alias("transaction_count"),
    F.sum("amount").alias("total_amount"),
    F.avg("amount").alias("average_amount")
)

print("\n--- DataFrame API Result ---")
dataframe_summary.show()

# Create temporary view
transactions_df.createOrReplaceTempView("transactions")

# Same analysis using Spark SQL
sql_summary = spark.sql("""
    SELECT
        transaction_type,
        COUNT(*) AS transaction_count,
        SUM(amount) AS total_amount,
        AVG(amount) AS average_amount
    FROM transactions
    GROUP BY transaction_type
""")

print("\n--- Spark SQL Result ---")
sql_summary.show()

spark.stop()