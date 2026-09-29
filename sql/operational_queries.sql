-- Query 1: Display all customers
SELECT *
FROM customer;


-- Query 2: Display all accounts with customer names
SELECT
    a.account_id,
    c.customer_name,
    a.account_type,
    a.account_status
FROM account a
JOIN customer c
    ON a.customer_id = c.customer_id;

    -- Query 3: Show all branches and their accounts
SELECT
    b.branch_id,
    b.branch_name,
    a.account_id,
    a.account_type
FROM branch b
JOIN account a
    ON b.branch_id = a.branch_id;


-- Query 4: Show all transactions with account and customer details
SELECT
    t.transaction_id,
    c.customer_name,
    t.account_id,
    t.transaction_type,
    t.amount,
    t.currency
FROM transactions t
JOIN account a
    ON t.account_id = a.account_id
JOIN customer c
    ON a.customer_id = c.customer_id;

    -- Query 5: Count accounts by account type
SELECT
    account_type,
    COUNT(*) AS account_count
FROM account
GROUP BY account_type;


-- Query 6: Calculate total transaction amount by transaction type
SELECT
    transaction_type,
    SUM(amount) AS total_amount
FROM transactions
GROUP BY transaction_type;

-- Query 7: Classify transactions based on amount
SELECT
    transaction_id,
    amount,
    CASE
        WHEN amount >= 500 THEN 'HIGH'
        WHEN amount >= 100 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS transaction_category
FROM transactions;


-- Query 8: Calculate total transaction amount for each customer
SELECT
    c.customer_id,
    c.customer_name,
    SUM(t.amount) AS total_transaction_amount
FROM customer c
JOIN account a
    ON c.customer_id = a.customer_id
JOIN transactions t
    ON a.account_id = t.account_id
GROUP BY
    c.customer_id,
    c.customer_name;

   

    -- Query 9: CTE to find customers with high transaction totals
WITH customer_totals AS (
    SELECT
        c.customer_id,
        c.customer_name,
        SUM(t.amount) AS total_amount
    FROM customer c
    JOIN account a
        ON c.customer_id = a.customer_id
    JOIN transactions t
        ON a.account_id = t.account_id
    GROUP BY
        c.customer_id,
        c.customer_name
)
SELECT
    customer_id,
    customer_name,
    total_amount
FROM customer_totals
WHERE total_amount >= 500;

-- Query 10: Rank transactions by amount
SELECT
    transaction_id,
    account_id,
    amount,
    RANK() OVER (
        ORDER BY amount DESC
    ) AS amount_rank
FROM transactions;


-- Query 11: Calculate running transaction total
SELECT
    transaction_id,
    account_id,
    transaction_date,
    amount,
    SUM(amount) OVER (
        ORDER BY transaction_date, transaction_id
    ) AS running_total
FROM transactions;

-- Query 12: Find customers who made more debit transactions than credit transactions
SELECT
    c.customer_id,
    c.customer_name,
    SUM(CASE
        WHEN t.transaction_type = 'DEBIT' THEN 1
        ELSE 0
    END) AS debit_count,
    SUM(CASE
        WHEN t.transaction_type = 'CREDIT' THEN 1
        ELSE 0
    END) AS credit_count
FROM customer c
JOIN account a
    ON c.customer_id = a.customer_id
JOIN transactions t
    ON a.account_id = t.account_id
GROUP BY
    c.customer_id,
    c.customer_name
HAVING debit_count > credit_count;