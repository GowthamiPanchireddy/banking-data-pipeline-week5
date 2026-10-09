from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


PROJECT_ROOT = Path(__file__).resolve().parents[2]

TRANSACTIONS_FILE = (
    PROJECT_ROOT
    / "data"
    / "generated"
    / "transactions_100k.csv"
)

ACCOUNTS_FILE = (
    PROJECT_ROOT
    / "data"
    / "reference"
    / "accounts.csv"
)


def create_spark():
    return (
        SparkSession.builder
        .appName("BankingSparkTests")
        .master("local[2]")
        .getOrCreate()
    )


def load_data(spark):
    transactions_df = spark.read.csv(
        str(TRANSACTIONS_FILE),
        header=True,
        inferSchema=True
    )

    accounts_df = spark.read.csv(
        str(ACCOUNTS_FILE),
        header=True,
        inferSchema=True
    )

    return transactions_df, accounts_df


def test_transaction_row_count():
    spark = create_spark()

    transactions_df, _ = load_data(spark)

    assert transactions_df.count() == 100000

    spark.stop()


def test_credit_transaction_count():
    spark = create_spark()

    transactions_df, _ = load_data(spark)

    credit_count = transactions_df.filter(
        F.col("transaction_type") == "CREDIT"
    ).count()

    assert credit_count == 50115

    spark.stop()


def test_duplicate_transaction_ids():
    spark = create_spark()

    transactions_df, _ = load_data(spark)

    duplicate_count = (
        transactions_df
        .groupBy("transaction_id")
        .count()
        .filter(F.col("count") > 1)
        .count()
    )

    assert duplicate_count == 0

    spark.stop()


def test_null_amounts():
    spark = create_spark()

    transactions_df, _ = load_data(spark)

    null_amount_count = transactions_df.filter(
        F.col("amount").isNull()
    ).count()

    assert null_amount_count == 0

    spark.stop()


def test_transaction_account_join_integrity():
    spark = create_spark()

    transactions_df, accounts_df = load_data(spark)

    invalid_account_count = (
        transactions_df
        .join(
            accounts_df.select("account_id"),
            "account_id",
            "left_anti"
        )
        .count()
    )

    assert invalid_account_count == 0

    spark.stop()