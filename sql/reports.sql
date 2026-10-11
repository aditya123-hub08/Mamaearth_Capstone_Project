USE mamaearth_capstone;

-- 3(a): Total orders, revenue and average order value

SELECT
    COUNT(*) AS total_orders,
    ROUND(
        SUM(
            o.quantity * p.price *
            (1 - COALESCE(o.discount_pct, 0) / 100)
        ),
        2
    ) AS total_revenue,
    ROUND(
        AVG(
            o.quantity * p.price *
            (1 - COALESCE(o.discount_pct, 0) / 100)
        ),
        2
    ) AS avg_order_value
FROM orders o
JOIN products p
    ON o.product_id = p.product_id;
    
 
-- 3(b): Rated vs unrated orders

SELECT
    COUNT(*) AS total_rows,
    COUNT(rating) AS rated_rows,
    COUNT(*) - COUNT(rating) AS unrated_rows
FROM orders;

-- 3(c): Customers with zero orders

SELECT
    c.customer_id,
    c.name
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;

-- 3(d): Return rate by city

SELECT
    c.city,
    COUNT(*) AS total_orders,
    SUM(o.returned) AS returned_orders,
    ROUND(
        100.0 * SUM(o.returned) / COUNT(*),
        1
    ) AS return_rate_pct
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY c.city
HAVING return_rate_pct > 20
ORDER BY return_rate_pct DESC;

-- 3(e): Top 5 customers by revenue

SELECT
    c.customer_id,
    c.name,
    ROUND(
        SUM(
            o.quantity * p.price *
            (1 - COALESCE(o.discount_pct, 0) / 100)
        ),
        2
    ) AS total_revenue
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN products p
    ON o.product_id = p.product_id
GROUP BY c.customer_id, c.name
ORDER BY total_revenue DESC
LIMIT 5;

-- Customers ranked 3rd to 5th

SELECT
    c.customer_id,
    c.name,
    ROUND(
        SUM(
            o.quantity * p.price *
            (1 - COALESCE(o.discount_pct, 0) / 100)
        ),
        2
    ) AS total_revenue
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
JOIN products p
    ON o.product_id = p.product_id
GROUP BY c.customer_id, c.name
ORDER BY total_revenue DESC
LIMIT 3 OFFSET 2;


-- 3(f): Revenue by product category

SELECT
    p.category,
    COUNT(*) AS order_count,
    ROUND(
        SUM(
            o.quantity * p.price *
            (1 - COALESCE(o.discount_pct, 0) / 100)
        ),
        2
    ) AS total_revenue
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;


-- 3(g): Customer names starting with A

SELECT
    name
FROM customers
WHERE name LIKE 'A%'
ORDER BY name;

-- 3(h): Distinct acquisition sources

SELECT DISTINCT
    acquisition_source
FROM customers
ORDER BY acquisition_source;

-- 3(i): Add loyalty tier

-- ALTER TABLE customers
-- ADD COLUMN loyalty_tier VARCHAR(10);

SET SQL_SAFE_UPDATES = 0;

UPDATE customers
SET loyalty_tier =
    CASE
        WHEN city_tier = 1 THEN 'Gold'
        ELSE 'Silver'
    END;

SET SQL_SAFE_UPDATES = 1;

SELECT
    loyalty_tier,
    COUNT(*) AS customer_count
FROM customers
GROUP BY loyalty_tier
ORDER BY loyalty_tier;