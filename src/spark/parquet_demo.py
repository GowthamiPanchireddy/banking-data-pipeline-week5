import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

spark = (
    SparkSession.builder
    .appName("BankingParquetDemo")
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

PARQUET_OUTPUT = os.path.join(
    PROJECT_ROOT,
    "output",
    "parquet",
    "transaction_summary"
)

transactions_df = spark.read.csv(
    TRANSACTIONS_FILE,
    header=True,
    inferSchema=True
)

summary_df = transactions_df.groupBy(
    "transaction_type"
).agg(
    F.count("*").alias("transaction_count"),
    F.sum("amount").alias("total_amount"),
    F.avg("amount").alias("average_amount")
)

print("\n--- DataFrame to Write ---")
summary_df.show()

print("\n--- Writing Parquet ---")

try:
    summary_df.write.mode("overwrite").parquet(PARQUET_OUTPUT)

    print("Parquet write: SUCCESS")

    print("\n--- Reading Parquet ---")
    parquet_df = spark.read.parquet(PARQUET_OUTPUT)
    parquet_df.show()

    print("Parquet row count:", parquet_df.count())

except Exception as error:
    print("Parquet write/read: NOT COMPLETED")
    print("Reason: Windows Hadoop filesystem configuration is missing.")
    print("Environment limitation:", error)

spark.stop()