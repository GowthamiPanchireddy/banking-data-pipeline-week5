-- Query 1: Transaction count and total amount by branch
SELECT
    branch_id,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_amount
FROM fact_transaction
GROUP BY branch_id;


-- Query 2: Transaction count and total amount by transaction type
SELECT
    transaction_type,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_amount
FROM fact_transaction
GROUP BY transaction_type;


-- Query 3: Customer transaction activity
SELECT
    c.customer_id,
    c.customer_name,
    COUNT(f.transaction_id) AS transaction_count,
    SUM(f.amount) AS total_amount
FROM fact_transaction f
JOIN dim_account a
    ON f.account_id = a.account_id
JOIN dim_customer c
    ON a.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name;


-- Query 4: Account transaction activity
SELECT
    a.account_id,
    a.account_type,
    COUNT(f.transaction_id) AS transaction_count,
    SUM(f.amount) AS total_amount
FROM fact_transaction f
JOIN dim_account a
    ON f.account_id = a.account_id
GROUP BY a.account_id, a.account_type;


-- Query 5: Transaction activity by date
SELECT
    date_key,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_amount
FROM fact_transaction
GROUP BY date_key
ORDER BY date_key;


-- Query 6: Transaction activity by branch and account type
SELECT
    b.branch_name,
    a.account_type,
    COUNT(f.transaction_id) AS transaction_count,
    SUM(f.amount) AS total_amount
FROM fact_transaction f
JOIN dim_branch b
    ON f.branch_id = b.branch_id
JOIN dim_account a
    ON f.account_id = a.account_id
GROUP BY b.branch_name, a.account_type;


-- Query 7: Credit and debit activity by customer
SELECT
    c.customer_name,
    f.transaction_type,
    COUNT(f.transaction_id) AS transaction_count,
    SUM(f.amount) AS total_amount
FROM fact_transaction f
JOIN dim_account a
    ON f.account_id = a.account_id
JOIN dim_customer c
    ON a.customer_id = c.customer_id
GROUP BY c.customer_name, f.transaction_type;


-- Query 8: High-value transactions
SELECT
    transaction_id,
    account_id,
    transaction_type,
    amount,
    date_key
FROM fact_transaction
WHERE amount >= 500
ORDER BY amount DESC;