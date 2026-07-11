-- =====================================================
-- ADVANCED SQL ANALYTICS
-- WINDOW FUNCTIONS AND CTEs
-- =====================================================


-- =====================================================
-- QUERY 1
-- RUNNING TOTAL OF MONTHLY REVENUE
-- =====================================================

WITH monthly_revenue AS (
    SELECT
        strftime('%Y-%m', o.order_date) AS order_month,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS revenue

    FROM orders o

    JOIN order_items oi
        ON o.order_id = oi.order_id

    WHERE o.status != 'CANCELLED'

    GROUP BY order_month
)

SELECT
    order_month,

    ROUND(revenue, 2) AS monthly_revenue,

    ROUND(
        SUM(revenue) OVER (
            ORDER BY order_month
        ),
        2
    ) AS running_total

FROM monthly_revenue

ORDER BY order_month;


-- =====================================================
-- QUERY 2
-- RANK CUSTOMERS BY LIFETIME VALUE
-- =====================================================

WITH customer_revenue AS (
    SELECT
        c.customer_id,
        c.customer_name,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS lifetime_value

    FROM customers c

    JOIN orders o
        ON c.customer_id = o.customer_id

    JOIN order_items oi
        ON o.order_id = oi.order_id

    WHERE o.status != 'CANCELLED'

    GROUP BY
        c.customer_id,
        c.customer_name
)

SELECT
    customer_id,
    customer_name,

    ROUND(
        lifetime_value,
        2
    ) AS lifetime_value,

    DENSE_RANK() OVER (
        ORDER BY lifetime_value DESC
    ) AS customer_rank

FROM customer_revenue

ORDER BY customer_rank;


-- =====================================================
-- QUERY 3
-- MONTHLY REVENUE GROWTH USING LAG
-- =====================================================

WITH monthly_revenue AS (
    SELECT
        strftime('%Y-%m', o.order_date) AS order_month,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS revenue

    FROM orders o

    JOIN order_items oi
        ON o.order_id = oi.order_id

    WHERE o.status != 'CANCELLED'

    GROUP BY order_month
),

revenue_with_previous AS (
    SELECT
        order_month,
        revenue,

        LAG(revenue) OVER (
            ORDER BY order_month
        ) AS previous_month_revenue

    FROM monthly_revenue
)

SELECT
    order_month,

    ROUND(
        revenue,
        2
    ) AS monthly_revenue,

    ROUND(
        previous_month_revenue,
        2
    ) AS previous_month_revenue,

    ROUND(
        (
            revenue - previous_month_revenue
        )
        * 100.0
        / NULLIF(
            previous_month_revenue,
            0
        ),
        2
    ) AS growth_percent

FROM revenue_with_previous

ORDER BY order_month;


-- =====================================================
-- QUERY 4
-- 3 MONTH MOVING AVERAGE OF REVENUE
-- =====================================================

WITH monthly_revenue AS (
    SELECT
        strftime('%Y-%m', o.order_date) AS order_month,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS revenue

    FROM orders o

    JOIN order_items oi
        ON o.order_id = oi.order_id

    WHERE o.status != 'CANCELLED'

    GROUP BY order_month
)

SELECT
    order_month,

    ROUND(
        revenue,
        2
    ) AS monthly_revenue,

    ROUND(
        AVG(revenue) OVER (
            ORDER BY order_month
            ROWS BETWEEN 2 PRECEDING
            AND CURRENT ROW
        ),
        2
    ) AS three_month_moving_average

FROM monthly_revenue

ORDER BY order_month;


-- =====================================================
-- QUERY 5
-- CUSTOMER SPEND SEGMENT USING NTILE
-- =====================================================

WITH customer_spending AS (
    SELECT
        c.customer_id,
        c.customer_name,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS total_spend

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

customer_tiers AS (
    SELECT
        customer_id,
        customer_name,
        total_spend,

        NTILE(3) OVER (
            ORDER BY total_spend
        ) AS spend_tier

    FROM customer_spending
)

SELECT
    customer_id,
    customer_name,

    ROUND(
        total_spend,
        2
    ) AS total_spend,

    CASE
        WHEN spend_tier = 1
            THEN 'LOW'

        WHEN spend_tier = 2
            THEN 'MEDIUM'

        WHEN spend_tier = 3
            THEN 'HIGH'
    END AS customer_segment

FROM customer_tiers

ORDER BY total_spend DESC;


-- =====================================================
-- QUERY 6
-- YEAR OVER YEAR REVENUE GROWTH
-- =====================================================

WITH yearly_revenue AS (
    SELECT
        strftime('%Y', o.order_date) AS order_year,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS revenue

    FROM orders o

    JOIN order_items oi
        ON o.order_id = oi.order_id

    WHERE o.status != 'CANCELLED'

    GROUP BY order_year
),

year_comparison AS (
    SELECT
        order_year,
        revenue,

        LAG(revenue) OVER (
            ORDER BY order_year
        ) AS previous_year_revenue

    FROM yearly_revenue
)

SELECT
    order_year,

    ROUND(
        revenue,
        2
    ) AS yearly_revenue,

    ROUND(
        previous_year_revenue,
        2
    ) AS previous_year_revenue,

    ROUND(
        (
            revenue - previous_year_revenue
        )
        * 100.0
        / NULLIF(
            previous_year_revenue,
            0
        ),
        2
    ) AS yoy_growth_percent

FROM year_comparison

ORDER BY order_year;


-- =====================================================
-- QUERY 7
-- CUSTOMER FIRST AND LAST PURCHASE DATE
-- USING WINDOW FUNCTIONS
-- =====================================================

WITH customer_orders AS (
    SELECT
        c.customer_id,
        c.customer_name,
        o.order_id,
        o.order_date,

        FIRST_VALUE(o.order_date) OVER (
            PARTITION BY c.customer_id
            ORDER BY o.order_date
        ) AS first_purchase_date,

        LAST_VALUE(o.order_date) OVER (
            PARTITION BY c.customer_id
            ORDER BY o.order_date
            ROWS BETWEEN UNBOUNDED PRECEDING
            AND UNBOUNDED FOLLOWING
        ) AS last_purchase_date

    FROM customers c

    JOIN orders o
        ON c.customer_id = o.customer_id
)

SELECT DISTINCT
    customer_id,
    customer_name,
    first_purchase_date,
    last_purchase_date

FROM customer_orders

ORDER BY customer_id;


-- =====================================================
-- QUERY 8
-- CUMULATIVE REVENUE DISTRIBUTION
-- =====================================================

WITH customer_revenue AS (
    SELECT
        c.customer_id,
        c.customer_name,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS revenue

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

cumulative_revenue AS (
    SELECT
        customer_id,
        customer_name,
        revenue,

        SUM(revenue) OVER (
            ORDER BY revenue DESC
        ) AS cumulative_revenue,

        SUM(revenue) OVER () AS total_revenue

    FROM customer_revenue
)

SELECT
    customer_id,
    customer_name,

    ROUND(
        revenue,
        2
    ) AS customer_revenue,

    ROUND(
        cumulative_revenue,
        2
    ) AS cumulative_revenue,

    ROUND(
        cumulative_revenue
        * 100.0
        / NULLIF(total_revenue, 0),
        2
    ) AS cumulative_revenue_percent

FROM cumulative_revenue

ORDER BY customer_revenue DESC;


-- =====================================================
-- QUERY 9
-- FREQUENTLY BOUGHT TOGETHER PRODUCTS
-- =====================================================

SELECT
    oi1.product_id AS product_1_id,
    p1.product_name AS product_1,

    oi2.product_id AS product_2_id,
    p2.product_name AS product_2,

    COUNT(
        DISTINCT oi1.order_id
    ) AS times_bought_together

FROM order_items oi1

JOIN order_items oi2
    ON oi1.order_id = oi2.order_id
    AND oi1.product_id < oi2.product_id

JOIN products p1
    ON oi1.product_id = p1.product_id

JOIN products p2
    ON oi2.product_id = p2.product_id

GROUP BY
    oi1.product_id,
    p1.product_name,
    oi2.product_id,
    p2.product_name

ORDER BY times_bought_together DESC

LIMIT 20;