from pathlib import Path
import logging

import pandas as pd

from src.ingestion.validation import validate_row


# -----------------------------
# Constants
# -----------------------------

INPUT_FOLDER = Path("data/raw")
OUTPUT_FOLDER = Path("output/summaries")

REQUIRED_COLUMNS = [
    "transaction_id",
    "account_id",
    "transaction_date",
    "transaction_type",
    "amount",
    "currency"
]


# -----------------------------
# Output folder
# -----------------------------

Path("output/logs").mkdir(parents=True, exist_ok=True)
Path("output/summaries").mkdir(parents=True, exist_ok=True)


# -----------------------------
# Logging setup
# -----------------------------

logging.basicConfig(
    filename=Path("output/logs/pipeline.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

logger.info("Pipeline started")


# -----------------------------
# File discovery
# -----------------------------

def discover_csv_files(input_folder):
    logger.info("CSV file discovery started")

    csv_files = list(input_folder.glob("*.csv"))

    for file in csv_files:
        logger.info(f"File discovered: {file.name}")

    return csv_files


# -----------------------------
# Schema checking
# -----------------------------

def check_required_columns(df):
    return [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]


# -----------------------------
# File reading
# -----------------------------

def read_csv_files(csv_files):
    dataframes = []
    rejected_files = []

    for file in csv_files:

        logger.info(f"Reading file: {file.name}")

        try:
            df = pd.read_csv(file)

        except (
            pd.errors.ParserError,
            UnicodeDecodeError,
            OSError
        ) as error:

            logger.error(
                f"Could not read file: {file.name} - {error}"
            )

            rejected_files.append(file.name)
            continue

        missing_columns = check_required_columns(df)

        if missing_columns:

            print(f"\nMissing columns in {file}:")
            print(missing_columns)

            logger.warning(
                f"Schema rejected: {file.name} - "
                f"Missing columns: {missing_columns}"
            )

            rejected_files.append(file.name)
            continue

        if df.empty:

            logger.warning(
                f"Empty/header-only file: {file.name}"
            )

        dataframes.append(df)

        logger.info(
            f"File read successfully: {file.name}"
        )

    return dataframes, rejected_files


# -----------------------------
# Duplicate handling
# -----------------------------

def find_duplicate_records(df):

    duplicate_mask = df[
        "transaction_id"
    ].duplicated(
        keep=False
    )

    return duplicate_mask


# -----------------------------
# Row validation
# -----------------------------

def validate_dataframe(df):

    df = df.copy()

    df["error_reason"] = ""

    for index, row in df.iterrows():

        errors = validate_row(row)

        if errors:

            df.loc[
                index,
                "error_reason"
            ] = "; ".join(errors)

    return df


# -----------------------------
# Add duplicate errors
# -----------------------------

def add_duplicate_errors(df):

    duplicate_mask = find_duplicate_records(df)

    df.loc[
        duplicate_mask,
        "error_reason"
    ] = df.loc[
        duplicate_mask,
        "error_reason"
    ].apply(
        lambda error:
        (
            error + "; Duplicate Transaction ID"
            if error
            else "Duplicate Transaction ID"
        )
    )

    return df


# -----------------------------
# Separate valid / invalid
# -----------------------------

def separate_valid_invalid(df):

    valid_df = df[
        df["error_reason"] == ""
    ].copy()

    invalid_df = df[
        df["error_reason"] != ""
    ].copy()

    return valid_df, invalid_df


# -----------------------------
# Write output files
# -----------------------------

def write_output_files(
    valid_df,
    invalid_df,
    output_folder
):

    valid_df.to_csv(
        output_folder / "valid_transactions.csv",
        index=False
    )

    invalid_df.to_csv(
        output_folder / "invalid_transactions.csv",
        index=False
    )

    logger.info("Valid and invalid output files created")


# -----------------------------
# Create summary
# -----------------------------

def create_summary(
    combined_df,
    valid_df,
    invalid_df,
    output_folder
):

    summary_df = pd.DataFrame({

        "metric": [
            "Total Records",
            "Valid Records",
            "Invalid Records"
        ],

        "count": [
            len(combined_df),
            len(valid_df),
            len(invalid_df)
        ]
    })

    summary_df.to_csv(
        output_folder / "summary.csv",
        index=False
    )

    return summary_df


# -----------------------------
# Create DQ summary
# -----------------------------

def create_dq_summary(
    csv_files,
    dataframes,
    rejected_files,
    combined_df,
    valid_df,
    invalid_df,
    output_folder
):

    duplicate_mask = find_duplicate_records(
        combined_df
    )

    dq_summary_df = pd.DataFrame({

        "metric": [

            "Files Discovered",
            "Files Read",
            "Files Rejected",
            "Total Records",
            "Valid Records",
            "Invalid Records",
            "Rejection Rate",
            "Duplicate Records",
            "Rejected Files"
        ],

        "value": [

            len(csv_files),

            len(dataframes),

            len(rejected_files),

            len(combined_df),

            len(valid_df),

            len(invalid_df),

            (
                len(invalid_df) / len(combined_df)
                if len(combined_df) > 0
                else 0
            ),

            duplicate_mask.sum(),

            ", ".join(rejected_files)
        ]
    })

    dq_summary_df.to_csv(
    Path("output/dq/dq_summary.csv"),
    index=False
)

    return dq_summary_df


# -----------------------------
# Main pipeline
# -----------------------------

def run_pipeline():

    csv_files = discover_csv_files(
        INPUT_FOLDER
    )

    print("CSV files found:")

    for file in csv_files:
        print(file)

    if not csv_files:

        logger.error(
            "No CSV files found in input folder"
        )

        print(
            "No CSV files found in input folder."
        )

        return

    dataframes, rejected_files = read_csv_files(
        csv_files
    )

    print("\nCSV files read successfully!")

    for df in dataframes:
        print(df.shape)

    if not dataframes:

        logger.error(
            "All candidate files were rejected"
        )

        print(
            "All candidate files were rejected."
        )

        return

    combined_df = pd.concat(
        dataframes,
        ignore_index=True
    )

    # Validate rows
    combined_df = validate_dataframe(
        combined_df
    )

    # Handle duplicates across all files
    combined_df = add_duplicate_errors(
        combined_df
    )

    # Separate valid and invalid
    valid_df, invalid_df = separate_valid_invalid(
        combined_df
    )

    print("\nValid Records:")
    print(valid_df)

    print("\nInvalid Records:")
    print(invalid_df)

    # Write outputs
    write_output_files(
        valid_df,
        invalid_df,
        OUTPUT_FOLDER
    )

    print(
        "\nOutput files created successfully!"
    )

    # Summary
    summary_df = create_summary(
        combined_df,
        valid_df,
        invalid_df,
        OUTPUT_FOLDER
    )

    # DQ summary
    dq_summary_df = create_dq_summary(
        csv_files,
        dataframes,
        rejected_files,
        combined_df,
        valid_df,
        invalid_df,
        OUTPUT_FOLDER
    )

    print(
        "\nDQ summary file created successfully!"
    )

    print(dq_summary_df)

    print(
        "\nSummary file created successfully!"
    )

    print(summary_df)

    logger.info(
        "Pipeline completed successfully"
    )


# -----------------------------
# Run
# -----------------------------

if __name__ == "__main__":
    run_pipeline()