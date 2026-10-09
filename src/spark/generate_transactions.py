import csv
import random
from datetime import date, timedelta
from pathlib import Path


# Reproducible random data
random.seed(42)


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

ACCOUNTS_FILE = PROJECT_ROOT / "data" / "reference" / "accounts.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "generated" / "transactions_100k.csv"


# Number of transactions
NUM_TRANSACTIONS = 100_000


# Read valid account IDs from existing banking data
with open(ACCOUNTS_FILE, "r", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    account_ids = [row["account_id"] for row in reader]


# Generate transactions
start_date = date(2026, 9, 7)

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
    fieldnames = [
        "transaction_id",
        "account_id",
        "transaction_date",
        "transaction_type",
        "amount",
        "currency",
    ]

    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    for i in range(1, NUM_TRANSACTIONS + 1):
        transaction_date = start_date + timedelta(
            days=random.randint(0, 90)
        )

        transaction_type = random.choice(["CREDIT", "DEBIT"])

        amount = round(random.uniform(10, 5000), 2)

        writer.writerow(
            {
                "transaction_id": f"SYN{i:06d}",
                "account_id": random.choice(account_ids),
                "transaction_date": transaction_date.isoformat(),
                "transaction_type": transaction_type,
                "amount": amount,
                "currency": "USD",
            }
        )


print(f"Generated {NUM_TRANSACTIONS} transactions.")
print(f"Output file: {OUTPUT_FILE}")