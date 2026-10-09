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

The original September 7 daily transaction file contained an incorrect account reference for transaction `T4004`.

The corrected September 7 file provided for the assignment was used for the final processing.

In the corrected file:

T4004 references account `A1002`.

Account `A1002` exists in the account reference data and belongs to branch `BR001`.

Therefore, T4004 is correctly represented in the analytical database with:

Account ID: `A1002`

Branch ID: `BR001`

Amount: `35.0`

The corrected file was processed successfully, and the final analytical database contains 20 unique transactions.

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


---

# Week 6 — PySpark Banking Analytics Pipeline

## Project Overview

In Week 6, the existing banking data engineering project was extended using PySpark.

The goal was to process banking data using Spark DataFrames and perform data quality checks, transformations, aggregations, joins, and analytical queries.

The project includes a reproducible synthetic dataset containing 100,000 banking transactions.

The existing Week 2–5 project work has been preserved.

## Technology Used

- Python 3.12.7
- PySpark 4.2.0
- Apache Spark 4.2.0
- Java 17
- pytest
- VS Code
- SQLite (existing Week 2–5 project)

## Spark Data Loading

The following banking datasets were loaded into Spark DataFrames:

- Transactions
- Accounts
- Customers
- Branches

The DataFrames were inspected using `show()`, `printSchema()`, and `count()`.

### Row Counts

| Dataset | Row Count |
|---|---:|
| Accounts | 10 |
| Customers | 6 |
| Branches | 3 |
| Synthetic Transactions | 100,000 |

## Spark Transformations

The following transformations were implemented using PySpark:

- `select()` — selects the required columns.
- `filter()` — filters CREDIT transactions.
- `filter()` — identifies high-value transactions.
- `withColumn()` — creates a derived column called `transaction_size`.

The high-value transaction threshold is 3000.

### Results

- CREDIT transactions: 50,115
- High-value transactions (amount > 3000): 40,036

The `filter()` and `withColumn()` operations are transformations. Spark evaluates them when an action is triggered.

## Spark Aggregations

PySpark `groupBy()` and aggregation functions were used to analyze banking transactions.

The following functions were used:

- `count()` — counts transactions.
- `sum()` — calculates total transaction amounts.
- `avg()` — calculates average transaction amounts.
- `groupBy()` — groups transactions by a selected column.

### Analysis Performed

- Summary by transaction type
- Summary by account
- Summary by branch

### Results by Transaction Type

| Transaction Type | Transaction Count |
|---|---:|
| CREDIT | 50,115 |
| DEBIT | 49,885 |
| Total | 100,000 |

The CREDIT and DEBIT amounts are stored as positive values. Therefore, total transaction amount does not automatically represent net cash flow or account balance.


## Spark Joins

PySpark joins were used to combine banking transaction data with account and branch information.

The project uses inner joins to connect:

- Transactions with Accounts
- Transaction summaries with Branches

The joined data helps analyze transaction activity by account, customer, and branch.

The transaction-to-account relationship was validated using a left anti join to identify transactions with invalid account IDs.

Result:

- Invalid account references: 0
- Branch-level transaction counts total: 100,000

## Spark Data Quality Checks

PySpark was used to validate the quality and integrity of the banking data.

The following checks were implemented:

- Null transaction IDs
- Null account IDs
- Null transaction amounts
- Duplicate transaction IDs
- Transactions referencing nonexistent accounts
- Accounts referencing nonexistent customers
- Accounts referencing nonexistent branches

### Data Quality Results

| Check | Error Count |
|---|---:|
| Null transaction IDs | 0 |
| Null account IDs | 0 |
| Null amounts | 0 |
| Duplicate transaction IDs | 0 |
| Invalid account references | 0 |
| Invalid customer references | 0 |
| Invalid branch references | 0 |

**Final Result: PASS**

Total data quality errors: 0

## Synthetic Banking Dataset

A Python program was created to generate 100,000 synthetic banking transactions.

Generator file:

`src/spark/generate_transactions.py`

Generated dataset:

`data/generated/transactions_100k.csv`

The generator uses a fixed random seed (`random.seed(42)`) to make the generated data reproducible.

Each transaction contains:

- Transaction ID
- Account ID
- Transaction date
- Transaction type
- Amount
- Currency

The generated transactions use account IDs from the existing account reference data.

## Spark SQL

The same transaction analysis was implemented using both the PySpark DataFrame API and Spark SQL.

A temporary view named `transactions` was created from the transactions DataFrame.

The analysis uses:

- `GROUP BY`
- `COUNT()`
- `SUM()`
- `AVG()`

Both approaches produced the same results.

| Transaction Type | Transaction Count |
|---|---:|
| CREDIT | 50,115 |
| DEBIT | 49,885 |

The DataFrame API uses methods such as `groupBy()` and `agg()`, while Spark SQL uses SQL statements to perform the same analysis.

## Spark Execution Concepts

The project demonstrates the following Apache Spark execution concepts.

### Transformation

A transformation creates a new DataFrame. Spark evaluates it lazily.

Example: `filter()`

### Action

An action triggers Spark execution and returns a result.

Example: `count()`

### Lazy Evaluation

Spark does not execute transformations immediately. It waits until an action is called.

### Partitions

Partitions are smaller chunks of data that Spark can process in parallel.

The transactions DataFrame reported 2 partitions in the local execution.

### Shuffle

A shuffle moves data between partitions.

In this project, `groupBy()` may cause a shuffle because data may need to move between partitions.

## Parquet Storage

A transaction summary DataFrame was prepared for Parquet storage.

The project attempted to write the summary to Parquet and read it back.

However, the operation could not be completed because the local Windows environment was missing the required Hadoop filesystem configuration.

The error was captured and documented. As allowed by the assignment, no additional Hadoop or unofficial Windows utilities were installed.

**Windows Environment Limitation:**
The Parquet write/read operation could not be completed because of a local Windows Hadoop filesystem configuration issue. Spark reported that `winutils.exe` was missing and `HADOOP_HOME` and `hadoop.home.dir` were not configured. The error was captured in `evidence/week6/parquet_results.txt`. This limitation is documented instead of spending additional time installing Windows Hadoop utilities.


Script: `src/spark/parquet_demo.py`

## PySpark Testing

Automated tests were created in:

`tests/spark/test_spark_pipeline.py`

The tests validate:

1. Expected transaction row count
2. CREDIT transaction count
3. Duplicate transaction IDs
4. Null transaction amounts
5. Transaction-to-account join integrity

### Test Execution

Run the Week 6 Spark tests using:

```powershell
py -3.12 -m pytest tests/spark/test_spark_pipeline.py -v


## How to Run Week 6

Run the following commands from the project root directory.

### 1. Generate Synthetic Transactions

```powershell
py -3.12 -m src.spark.generate_transactions
```

This generates 100,000 synthetic banking transactions.

### 2. Load Banking Data

```powershell
py -3.12 -m src.spark.load_data
```

Loads transactions, accounts, customers, and branches into PySpark DataFrames.

### 3. Run Transformations

```powershell
py -3.12 -m src.spark.transformations
```

Demonstrates column selection, filtering, and derived columns.

### 4. Run Analytics and Joins

```powershell
py -3.12 -m src.spark.analytics
```

Performs aggregations and joins banking transactions with account and branch information.

### 5. Run Data Quality Checks

```powershell
py -3.12 -m src.spark.data_quality
```

Checks null values, duplicate transaction IDs, and invalid account, customer, and branch references.

### 6. Compare DataFrame API and Spark SQL

```powershell
py -3.12 -m src.spark.spark_sql_analysis
```

Runs equivalent transaction summaries using both approaches.

### 7. Review Execution Concepts

```powershell
py -3.12 -m src.spark.execution_concepts
```

Demonstrates transformations, actions, partitions, and shuffle concepts.

### 8. Test the Pipeline

```powershell
py -3.12 -m pytest tests/spark/test_spark_pipeline.py -v
```

Runs the Week 6 PySpark tests.

### 9. Run the Parquet Demonstration

```powershell
py -3.12 -m src.spark.parquet_demo
```

Attempts to write and read a Parquet summary. See the Parquet Storage section for the documented Windows environment limitation.


## Week 6 — Understanding Questions and Answers

### 1. What is PySpark?

PySpark is the Python API for Apache Spark. It is used to process and analyze large datasets.

### 2. What is a DataFrame?

A DataFrame is a distributed collection of data organized into named columns.

### 3. What is the difference between a transformation and an action?

A transformation creates a new DataFrame, while an action triggers execution and returns a result or writes data.

### 4. What is lazy evaluation?

Lazy evaluation means Spark waits to execute transformations until an action is called.

### 5. What is a partition?

A partition is a smaller portion of a dataset that Spark can process separately.

### 6. What is a shuffle?

A shuffle moves data between partitions, often during operations such as `groupBy()` and some joins.

### 7. What is the difference between the DataFrame API and Spark SQL?

The DataFrame API uses Python methods such as `groupBy()` and `agg()`. Spark SQL uses SQL statements such as `GROUP BY`, `COUNT()`, and `SUM()`.

In this project, both approaches produced the same transaction summary.

### 8. What is data quality checking?

Data quality checking identifies problems such as null values, duplicate transaction IDs, and invalid references between related datasets.

In this project, all seven implemented data quality checks passed for the generated dataset.

### 9. Why use Parquet?

Parquet is a column-oriented file format commonly used for analytical workloads. This project attempted to demonstrate writing and reading a Parquet summary, but the operation was blocked by a documented Windows Hadoop filesystem configuration issue.

### 10. Why generate 100,000 synthetic transactions?

The synthetic dataset provides a repeatable, larger dataset for practicing PySpark transformations, aggregations, joins, and testing without depending on real customer transactions.

