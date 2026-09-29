# Week 5 Analytics Architecture

```text
data/raw + data/reference
          |
          v
   Ingestion Pipeline
          |
          v
   data/validated
          |
          v
   Operational Database
     banking.db
          |
          v
    Analytics Build
          |
          v
   Analytical Database
     analytics.db
          |
          v
     Star Schema

              dim_customer
                    |
dim_branch ---- fact_transaction ---- dim_account
                    |
                 dim_date


Data Flow

Raw transaction files and reference data are processed by the ingestion pipeline. Valid transactions are stored in the validated folder and loaded into the operational database.

The analytics build process reads the operational data and creates a separate analytical database using a star schema.

Fact Table Grain

One row in fact_transaction represents one banking transaction.

Main Tables
dim_customer – customer information
dim_account – account information
dim_branch – branch information
dim_date – date information
fact_transaction – transaction-level facts