import pandas as pd
from pathlib import Path

from src.ingestion.pipeline import (
    discover_csv_files,
    read_csv_files,
    validate_dataframe,
    add_duplicate_errors,
    separate_valid_invalid
)


def test_cross_file_duplicate():
    df1 = pd.DataFrame({
        "transaction_id": ["T1001"],
        "account_id": ["A1001"],
        "transaction_date": ["2026-09-06"],
        "transaction_type": ["CREDIT"],
        "amount": [500],
        "currency": ["USD"]
    })

    df2 = pd.DataFrame({
        "transaction_id": ["T1001"],
        "account_id": ["A2001"],
        "transaction_date": ["2026-09-06"],
        "transaction_type": ["DEBIT"],
        "amount": [300],
        "currency": ["USD"]
    })

    combined = pd.concat(
        [df1, df2],
        ignore_index=True
    )

    combined = validate_dataframe(combined)

    result = add_duplicate_errors(combined)

    assert "Duplicate Transaction ID" in result.loc[0, "error_reason"]
    assert "Duplicate Transaction ID" in result.loc[1, "error_reason"]


def test_multiple_validation_errors():
    errors = [
        "Account ID is missing",
        "Invalid transaction type",
        "Amount must be greater than 0",
        "Invalid currency"
    ]

    error_reason = "; ".join(errors)

    assert "Account ID is missing" in error_reason
    assert "Invalid transaction type" in error_reason
    assert "Amount must be greater than 0" in error_reason
    assert "Invalid currency" in error_reason


def test_original_dataset_regression():

    input_folder = Path("data/raw")

    csv_files = discover_csv_files(
        input_folder
    )

    original_files = [
        file for file in csv_files
        if file.name in [
            "BR001_20260906_TRANSACTION.csv",
            "BR002_20260906_TRANSACTION.csv",
            "BR003_20260906_TRANSACTION.csv"
        ]
    ]

    dataframes, rejected_files = read_csv_files(
        original_files
    )

    combined_df = pd.concat(
        dataframes,
        ignore_index=True
    )

    combined_df = validate_dataframe(
        combined_df
    )

    combined_df = add_duplicate_errors(
        combined_df
    )

    valid_df, invalid_df = separate_valid_invalid(
        combined_df
    )

    assert len(combined_df) == 24
    assert len(valid_df) == 10
    assert len(invalid_df) == 14
    assert len(rejected_files) == 0