# Banking Data Engineering Pipeline – Week 5

## Project Overview

This project implements a simple banking data engineering pipeline using Python, SQLite, SQL, and pytest.

The project extends the earlier banking data pipeline and database work by adding:

* Daily incremental transaction loading
* UPSERT-based correction handling
* Rerun-safe processing
* Operational banking database
* Analytical database with a star schema
* Analytical SQL queries
* Data quality and validation checks
* Automated tests

The project is designed using simple Python and SQLite without using Spark, Airflow, dbt, Docker, cloud services, or server-based databases.

---

## Technology Used

* Python 3.10
* SQLite
* SQL
* pandas
* pytest
* VS Code

---

## Project Structure

```text
banking-data-pipeline week5/
│
├── config/
│
├── data/
│   ├── raw/
│   │   ├── BR001_20260906_TRANSACTION.csv
│   │   ├── BR002_20260906_TRANSACTION.csv
│   │   └── BR003_20260906_TRANSACTION.csv
│   │
│   ├── reference/
│   │   ├── customers.csv
│   │   ├── accounts.csv
│   │   └── branches.csv
│   │
│   ├── validated/
│   │   ├── valid_transactions.csv
│   │   └── invalid_transactions.csv
│   │
│   └── daily/
│       ├── transactions_20260907.csv
│       ├── transactions_20260908.csv
│       └── transactions_20260909.csv
│
├── src/
│   ├── ingestion/
│   │   ├── pipeline.py
│   │   └── validation.py
│   │
│   ├── operational/
│   │   ├── database.py
│   │   └── incremental_load.py
│   │
│   └── analytics/
│       └── build_analytics.py
│
├── output/
│   ├── logs/
│   ├── dq/
│   └── summaries/
│
├── database/
│   ├── banking.db
│   └── analytics.db
│
├── sql/
│   ├── operational_queries.sql
│   └── analytical_queries.sql
│
├── tests/
│   ├── test_validation.py
│   ├── test_pipeline.py
│   ├── test_database.py
│   └── test_week5.py
│
├── evidence/
│
├── docs/
│
├── README.md
└── requirements.txt
```

---

## Data Flow

```text
data/raw + data/reference
          |
          v
   src/ingestion
          |
          +------> data/validated
          |
          +------> output/logs
          |
          +------> output/dq
          |
          +------> output/summaries
          |
          v
database/banking.db
          |
          v
src/analytics
          |
          v
database/analytics.db
          |
          v
sql/analytical_queries.sql
```

---

## Folder Responsibilities

### `data/raw`

Contains the original transaction files from the earlier pipeline.

### `data/reference`

Contains reference/master data:

* Customers
* Accounts
* Branches

### `data/validated`

Contains validated and invalid transaction outputs.

### `data/daily`

Contains trusted daily transaction files for incremental processing.

### `src/ingestion`

Contains ingestion and validation logic.

### `src/operational`

Contains the operational database logic and incremental transaction loading.

### `src/analytics`

Builds the analytical database from the operational database.

### `output`

Contains logs, data-quality results, and pipeline summaries.

### `database`

Contains:

* `banking.db` – operational database
* `analytics.db` – analytical database

### `sql`

Contains operational and analytical SQL queries.

### `tests`

Contains automated tests for validation, pipeline, database, and Week 5 analytics.

---

## Requirements

Install the required packages using:

```powershell
pip install -r requirements.txt
```

Requirements:

```text
pandas==2.3.3
pytest==9.1.1
```

---

## Pipeline Execution

Run the ingestion pipeline:

```powershell
python -m src.ingestion.pipeline
```

The pipeline reads the raw transaction files, validates the records, detects duplicates, and creates validation and summary outputs.

---

## Operational Database

The operational database is:

```text
database/banking.db
```

It contains the following tables:

* `customer`
* `branch`
* `account`
* `transactions`

The transaction table has one row for each banking transaction.

---

## Incremental Loading

Daily transaction files are processed in date order:

```text
transactions_20260907.csv
transactions_20260908.csv
transactions_20260909.csv
```

The incremental loader uses SQLite UPSERT logic.

```sql
INSERT INTO transactions (...)
VALUES (...)
ON CONFLICT(transaction_id)
DO UPDATE SET
    account_id = excluded.account_id,
    transaction_date = excluded.transaction_date,
    transaction_type = excluded.transaction_type,
    amount = excluded.amount,
    currency = excluded.currency;
```

### New Transaction

If the transaction ID does not exist, the transaction is inserted.

### Existing Transaction

If the transaction ID already exists, the incoming trusted row updates the existing transaction.

This allows later files to correct previously stored transaction values.

### Rerun Behavior

Running the same daily file again does not create duplicate transaction IDs.

Corrections remain applied after rerunning the same file.

---

## Incremental Processing Results

The daily files produced the following changes:

### 2026-09-07

New transactions:

* T4001
* T4002
* T4003
* T4004

Transaction count increased from 10 to 14.

### 2026-09-08

New transactions:

* T4005
* T4006
* T4007

Correction:

* T1001 amount changed from 500.0 to 550.0

Transaction count became 17.

Rerunning the same file kept the transaction count at 17 and preserved the T1001 correction.

### 2026-09-09

New transactions:

* T4008
* T4009
* T4010

Correction:

* T4002 amount changed from 50.0 to 55.0

Final operational transaction count:

```text
20
```

---

## Analytical Database

The analytical database is:

```text
database/analytics.db
```

It contains a simple star schema.

```text
              dim_date
                 |
                 |
dim_branch -- fact_transaction -- dim_account
                 |
                 |
            dim_customer
```

### Dimension Tables

* `dim_customer`
* `dim_account`
* `dim_branch`
* `dim_date`

### Fact Table

* `fact_transaction`

### Fact Grain

The grain of `fact_transaction` is:

> One row represents one banking transaction.

The final fact table contains:

```text
20 transactions
```

Transaction IDs are unique.

---

## Analytics

The analytical SQL contains 8 queries covering:

1. Transaction count and total amount by branch
2. Transaction count and total amount by transaction type
3. Customer transaction activity
4. Account transaction activity
5. Transaction activity by date
6. Transaction activity by branch and account type
7. Credit and debit activity by customer
8. High-value transactions

---

## Important Analytical Result

The final analytical database contains:

```text
CREDIT transactions: 11
Total CREDIT amount: 4060.0

DEBIT transactions: 9
Total DEBIT amount: 675.5
```

The amount is treated as the transaction amount. Since CREDIT and DEBIT are represented as positive amounts, the total amount should not automatically be interpreted as net cash flow or account balance.

---

## Data Quality Consideration

One daily transaction, `T4004`, references account `A1005`, which is not present in the existing account reference data.

The transaction is preserved in the fact table to maintain the required transaction grain.

Its branch reference is therefore `NULL` rather than inventing a branch or account record.

This is documented as a data-quality/reference-data limitation.

---

## Testing

Run all tests using:

```powershell
python -m pytest -v
```

Final test result:

```text
17 passed
```

The tests cover:

* Database tables
* Foreign key enforcement
* Expected row counts
* Duplicate primary-key rejection
* Invalid foreign-key rejection
* Invalid amount rejection
* Rerun stability
* Cross-file duplicate detection
* Validation errors
* Original dataset regression
* Fact transaction count
* Unique transaction IDs
* Known transaction correction
* Known analytical result

---

## Run Order

Recommended execution order:

### 1. Run ingestion

```powershell
python -m src.ingestion.pipeline
```

### 2. Load daily files incrementally

```powershell
python -m src.operational.incremental_load
```

The daily file path in `incremental_load.py` should be changed for each daily input when processing the files in date order.

### 3. Build the analytical database

```powershell
python -m src.analytics.build_analytics
```

### 4. Run tests

```powershell
python -m pytest -v
```

---

## Operational SQL

Operational queries are stored in:

```text
sql/operational_queries.sql
```

These queries are used to inspect customers, accounts, branches, transactions, transaction totals, classifications, and customer transaction activity.

---

## Analytical SQL

Analytical queries are stored in:

```text
sql/analytical_queries.sql
```

These queries operate on the analytical star schema.

---

## Data Lineage

```text
Raw Transaction Files
        |
        v
Validation and Data Quality
        |
        v
Validated Transaction Data
        |
        v
Operational Database
(banking.db)
        |
        v
Analytics Build
        |
        v
Analytical Database
(analytics.db)
        |
        v
Analytical SQL Queries
```

---

## Key Concepts

### UPSERT

UPSERT means inserting a new row when the key does not exist and updating the existing row when the key already exists.

### `excluded`

In SQLite UPSERT syntax, `excluded` refers to the incoming row that caused the conflict.

### Incremental Load

An incremental load processes only new or newly supplied data instead of rebuilding the complete dataset from the beginning.

### Rerun Safety

A rerun should not create duplicate records and should preserve valid corrections.

### Fact Table

A fact table stores measurable business events.

In this project:

```text
fact_transaction
```

stores banking transactions.

### Dimension Table

A dimension table stores descriptive information used to provide context to facts.

Examples:

```text
dim_customer
dim_account
dim_branch
dim_date
```

### Grain

Grain defines what one row represents.

For this project:

> One row in `fact_transaction` represents one banking transaction.

---

## Limitations

* SQLite is used for simplicity and local development.
* No distributed processing framework is used.
* No workflow orchestration tool is used.
* The incremental loader does not maintain historical versions of corrected rows.
* The current correction strategy assumes the incoming trusted row is the correct version.
* The project does not implement a full audit-history table.
* Reference-data issues such as missing account `A1005` are preserved and documented rather than automatically invented or repaired.

---

## Conclusion

This Week 5 project demonstrates a complete beginner-friendly banking data engineering workflow using Python, SQLite, SQL, and pytest.

The pipeline supports:

* Data ingestion
* Validation
* Operational database loading
* Incremental processing
* UPSERT-based corrections
* Rerun-safe loading
* Analytical star-schema construction
* Analytical SQL
* Automated testing
* Data-quality documentation
