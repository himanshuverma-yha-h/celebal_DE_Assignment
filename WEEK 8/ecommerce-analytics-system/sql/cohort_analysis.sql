-- =====================================================
-- COHORT, RETENTION AND CUSTOMER SEGMENTATION ANALYSIS
-- =====================================================


-- =====================================================
-- QUERY 1
-- CUSTOMER COHORT BY FIRST PURCHASE MONTH
-- =====================================================

WITH customer_first_purchase AS (
    SELECT
        customer_id,
        MIN(order_date) AS first_purchase_date
    FROM orders
    GROUP BY customer_id
)

SELECT
    strftime(
        '%Y-%m',
        first_purchase_date
    ) AS cohort_month,

    COUNT(customer_id) AS customers_in_cohort

FROM customer_first_purchase

GROUP BY cohort_month

ORDER BY cohort_month;


-- =====================================================
-- QUERY 2
-- MONTHLY COHORT RETENTION
-- =====================================================

WITH customer_first_purchase AS (
    SELECT
        customer_id,
        MIN(order_date) AS first_purchase_date
    FROM orders
    GROUP BY customer_id
),

customer_activity AS (
    SELECT DISTINCT
        o.customer_id,

        strftime(
            '%Y-%m',
            cfp.first_purchase_date
        ) AS cohort_month,

        strftime(
            '%Y-%m',
            o.order_date
        ) AS activity_month,

        (
            (
                CAST(strftime('%Y', o.order_date) AS INTEGER)
                -
                CAST(strftime('%Y', cfp.first_purchase_date) AS INTEGER)
            ) * 12

            +

            (
                CAST(strftime('%m', o.order_date) AS INTEGER)
                -
                CAST(strftime('%m', cfp.first_purchase_date) AS INTEGER)
            )
        ) AS month_number

    FROM orders o

    JOIN customer_first_purchase cfp
        ON o.customer_id = cfp.customer_id
),

cohort_size AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) AS total_customers

    FROM customer_activity

    WHERE month_number = 0

    GROUP BY cohort_month
),

retention AS (
    SELECT
        cohort_month,
        month_number,

        COUNT(
            DISTINCT customer_id
        ) AS retained_customers

    FROM customer_activity

    GROUP BY
        cohort_month,
        month_number
)

SELECT
    r.cohort_month,
    r.month_number,
    r.retained_customers,
    cs.total_customers,

    ROUND(
        r.retained_customers
        * 100.0
        / NULLIF(cs.total_customers, 0),
        2
    ) AS retention_rate_percent

FROM retention r

JOIN cohort_size cs
    ON r.cohort_month = cs.cohort_month

ORDER BY
    r.cohort_month,
    r.month_number;


-- =====================================================
-- QUERY 3
-- REPEAT VS ONE-TIME CUSTOMERS
-- =====================================================

WITH customer_orders AS (
    SELECT
        customer_id,

        COUNT(
            DISTINCT order_id
        ) AS order_count

    FROM orders

    GROUP BY customer_id
)

SELECT
    CASE
        WHEN order_count = 1
            THEN 'ONE-TIME CUSTOMER'

        ELSE 'REPEAT CUSTOMER'
    END AS customer_status,

    COUNT(*) AS total_customers

FROM customer_orders

GROUP BY customer_status;


-- =====================================================
-- QUERY 4
-- CHURNED VS ACTIVE CUSTOMERS
-- =====================================================

WITH customer_last_purchase AS (
    SELECT
        customer_id,
        MAX(order_date) AS last_purchase_date

    FROM orders

    GROUP BY customer_id
)

SELECT
    CASE
        WHEN date(last_purchase_date)
             < date('now', '-6 months')
            THEN 'CHURNED'

        ELSE 'ACTIVE'
    END AS customer_status,

    COUNT(customer_id) AS total_customers

FROM customer_last_purchase

GROUP BY customer_status;


-- =====================================================
-- QUERY 5
-- PURCHASE FREQUENCY SEGMENTATION
-- =====================================================

WITH customer_frequency AS (
    SELECT
        c.customer_id,
        c.customer_name,

        COUNT(
            DISTINCT o.order_id
        ) AS total_orders

    FROM customers c

    LEFT JOIN orders o
        ON c.customer_id = o.customer_id

    GROUP BY
        c.customer_id,
        c.customer_name
)

SELECT
    customer_id,
    customer_name,
    total_orders,

    CASE
        WHEN total_orders <= 1
            THEN 'ONE-TIME'

        WHEN total_orders BETWEEN 2 AND 4
            THEN 'OCCASIONAL'

        ELSE 'LOYAL'
    END AS frequency_segment

FROM customer_frequency

ORDER BY total_orders DESC;


-- =====================================================
-- QUERY 6
-- RFM CUSTOMER SEGMENTATION
-- =====================================================

WITH customer_metrics AS (
    SELECT
        c.customer_id,
        c.customer_name,

        CAST(
            julianday('now')
            -
            julianday(MAX(o.order_date))
            AS INTEGER
        ) AS recency_days,

        COUNT(
            DISTINCT o.order_id
        ) AS frequency,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS monetary

    FROM customers c

    JOIN orders o
        ON c.customer_id = o.customer_id

    JOIN order_items oi
        ON o.order_id = oi.order_id

    WHERE o.status != 'CANCELLED'

    GROUP BY
        c.customer_id,
        c.customer_name
),

rfm_scores AS (
    SELECT
        customer_id,
        customer_name,
        recency_days,
        frequency,
        monetary,

        NTILE(3) OVER (
            ORDER BY recency_days DESC
        ) AS recency_score,

        NTILE(3) OVER (
            ORDER BY frequency
        ) AS frequency_score,

        NTILE(3) OVER (
            ORDER BY monetary
        ) AS monetary_score

    FROM customer_metrics
)

SELECT
    customer_id,
    customer_name,
    recency_days,
    frequency,

    ROUND(
        monetary,
        2
    ) AS monetary,

    recency_score,
    frequency_score,
    monetary_score,

    CASE
        WHEN recency_score = 3
             AND frequency_score = 3
             AND monetary_score = 3
            THEN 'BEST CUSTOMERS'

        WHEN recency_score >= 2
             AND frequency_score >= 2
            THEN 'LOYAL CUSTOMERS'

        WHEN recency_score = 1
            THEN 'AT RISK'

        ELSE 'REGULAR CUSTOMERS'
    END AS rfm_segment

FROM rfm_scores

ORDER BY
    monetary DESC;