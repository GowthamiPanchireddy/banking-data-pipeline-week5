import pandas as pd


def validate_amount(amount):
    numeric_amount = pd.to_numeric(amount, errors="coerce")

    if pd.isna(numeric_amount):
        return "Amount must be numeric"

    if numeric_amount <= 0:
        return "Amount must be greater than 0"

    return ""


def validate_transaction_type(transaction_type):
    if transaction_type not in ["CREDIT", "DEBIT"]:
        return "Invalid transaction type"

    return ""


def validate_transaction_date(transaction_date):
    try:
        pd.to_datetime(
            transaction_date,
            format="%Y-%m-%d"
        )
        return ""
    except (ValueError, TypeError):
        return "Invalid transaction date"


def validate_currency(currency):
    if currency != "USD":
        return "Invalid currency"

    return ""


def validate_required_value(value, field_name):
    if pd.isna(value) or value == "":
        return f"{field_name} is missing"

    return ""


def validate_row(row):
    errors = []

    # Transaction ID
    error = validate_required_value(
        row["transaction_id"],
        "Transaction ID"
    )

    if error:
        errors.append(error)

    # Account ID
    error = validate_required_value(
        row["account_id"],
        "Account ID"
    )

    if error:
        errors.append(error)

    # Transaction Date
    error = validate_required_value(
        row["transaction_date"],
        "Transaction Date"
    )

    if error:
        errors.append(error)
    else:
        error = validate_transaction_date(
            row["transaction_date"]
        )

        if error:
            errors.append(error)

    # Transaction Type
    error = validate_transaction_type(
        row["transaction_type"]
    )

    if error:
        errors.append(error)

    # Amount
    error = validate_required_value(
        row["amount"],
        "Amount"
    )

    if error:
        errors.append(error)
    else:
        error = validate_amount(
            row["amount"]
        )

        if error:
            errors.append(error)

    # Currency
    error = validate_currency(
        row["currency"]
    )

    if error:
        errors.append(error)

    return errors