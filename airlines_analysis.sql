SELECT
    COUNT(*) AS total_flights,
    SUM(CASE WHEN overall_quality = 'Valid' THEN 1 ELSE 0 END) AS valid_flights,
    SUM(CASE WHEN overall_quality = 'Anomaly' THEN 1 ELSE 0 END) AS anomalous_flights,
    SUM(CASE WHEN overnight = 1 THEN 1 ELSE 0 END) AS overnight_flights
FROM dim_flight;


SELECT
    COUNT(*) AS total_bookings,
    SUM(CASE WHEN status = 'CONFIRMED' THEN 1 ELSE 0 END) AS confirmed_bookings,
    SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END) AS cancelled_bookings,
    SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) AS pending_bookings,
    SUM(CASE WHEN status = 'Unknown' THEN 1 ELSE 0 END) AS unknown_bookings
FROM fact_booking;


SELECT
    ROUND(
        SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*),
        2
    ) AS cancellation_rate
FROM fact_booking;


SELECT
    airline,
    COUNT(*) AS total_flights
FROM dim_flight
WHERE overall_quality = 'Valid'
GROUP BY airline
ORDER BY total_flights DESC;


SELECT
    airline,
    ROUND(
        AVG(
            CAST(substr(duration, 1, 2) AS INTEGER) * 60 +
            CAST(substr(duration, 4, 2) AS INTEGER) +
            CAST(substr(duration, 7, 2) AS INTEGER) / 60.0
        ),
        2
    ) AS average_duration_minutes
FROM dim_flight
WHERE overall_quality = 'Valid'
GROUP BY airline
ORDER BY average_duration_minutes DESC;


SELECT
    source,
    destination,
    COUNT(*) AS total_flights
FROM dim_flight
WHERE overall_quality = 'Valid'
GROUP BY source, destination
ORDER BY total_flights DESC
LIMIT 10;


SELECT
    status,
    COUNT(*) AS bookings,
    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM fact_booking),
        1
    ) AS percentage
FROM fact_booking
GROUP BY status
ORDER BY bookings DESC;


SELECT
    DATE(booking_date) AS booking_date,
    COUNT(*) AS total_bookings,
    SUM(CASE WHEN status = 'CONFIRMED' THEN 1 ELSE 0 END) AS confirmed,
    SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END) AS cancelled,
    SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) AS pending
FROM fact_booking
GROUP BY DATE(booking_date)
ORDER BY DATE(booking_date);


SELECT
    COUNT(*) AS total_payments,
    SUM(CASE WHEN amount_quality = 'Valid' THEN 1 ELSE 0 END) AS valid_payments,
    SUM(CASE WHEN amount_quality = 'Missing/Invalid' THEN 1 ELSE 0 END) AS invalid_payments,
    ROUND(
        SUM(
            CASE
                WHEN amount_quality = 'Valid' THEN amount
                ELSE 0
            END
        ),
        2
    ) AS total_revenue
FROM fact_payment;


SELECT
    ROUND(AVG(amount), 2) AS average_payment,
    ROUND(MIN(amount), 2) AS minimum_payment,
    ROUND(MAX(amount), 2) AS maximum_payment
FROM fact_payment
WHERE amount_quality = 'Valid';


SELECT
    payment_method,
    COUNT(*) AS total_payments,
    SUM(
        CASE
            WHEN amount_quality = 'Valid' THEN 1
            ELSE 0
        END
    ) AS valid_payments,
    ROUND(
        SUM(
            CASE
                WHEN amount_quality = 'Valid' THEN amount
                ELSE 0
            END
        ),
        2
    ) AS revenue
FROM fact_payment
GROUP BY payment_method
ORDER BY revenue DESC;


SELECT
    'Flights' AS dataset,
    COUNT(*) AS total_records,
    SUM(
        CASE WHEN overall_quality = 'Valid'
        THEN 1 ELSE 0 END
    ) AS valid_records,
    SUM(
        CASE WHEN overall_quality = 'Anomaly'
        THEN 1 ELSE 0 END
    ) AS anomalous_records
FROM dim_flight

UNION ALL

SELECT
    'Bookings',
    COUNT(*),
    SUM(
        CASE WHEN status_quality = 'Valid'
        THEN 1 ELSE 0 END
    ),
    SUM(
        CASE WHEN status_quality = 'Missing/Invalid'
        THEN 1 ELSE 0 END
    )
FROM fact_booking

UNION ALL

SELECT
    'Payments',
    COUNT(*),
    SUM(
        CASE WHEN amount_quality = 'Valid'
        THEN 1 ELSE 0 END
    ),
    SUM(
        CASE WHEN amount_quality = 'Missing/Invalid'
        THEN 1 ELSE 0 END
    )
FROM fact_payment;