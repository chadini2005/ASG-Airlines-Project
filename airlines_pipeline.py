import os
import pandas as pd
from sqlalchemy import create_engine, text

file = "data/raw/UseCase - Airlines.xlsx"

os.makedirs("cleaned_data", exist_ok=True)

flights = pd.read_excel(file, sheet_name="flights")
bookings = pd.read_excel(file, sheet_name="bookings")
passengers = pd.read_excel(file, sheet_name="passengers")
payments = pd.read_excel(file, sheet_name="payments")

print("Excel data loaded successfully!")

df_clean = flights.drop_duplicates().copy()

df_clean["airline"] = df_clean["airline"].fillna("Unknown")
df_clean["airline"] = df_clean["airline"].replace("UNKNOWN", "Unknown")

df_clean["departure_time"] = pd.to_datetime(df_clean["departure_time"])
df_clean["arrival_time"] = pd.to_datetime(df_clean["arrival_time"])

df_clean["overnight"] = (
    df_clean["arrival_time"].dt.date >
    df_clean["departure_time"].dt.date
)

calculated_duration = (
    df_clean["arrival_time"] -
    df_clean["departure_time"]
)

negative = calculated_duration < pd.Timedelta(0)

df_clean["time_quality"] = "Valid"
df_clean.loc[negative, "time_quality"] = "Invalid"

provided_duration = df_clean["duration"].apply(
    lambda x: pd.Timedelta(
        hours=x.hour,
        minutes=x.minute,
        seconds=x.second
    )
)

duration_difference = abs(
    provided_duration - calculated_duration
)

df_clean["duration_mismatch"] = (
    duration_difference > pd.Timedelta(minutes=5)
)

df_clean["overall_quality"] = "Valid"

df_clean.loc[
    (df_clean["time_quality"] == "Invalid") |
    (df_clean["duration_mismatch"]),
    "overall_quality"
] = "Anomaly"

df_clean["flight_id_valid"] = (
    df_clean["flight_id"]
    .astype(str)
    .str.match(r"^[A-Z0-9]{2}\d{3}$")
)

df_clean["duplicate_flight_id"] = (
    df_clean["flight_id"].duplicated(keep=False)
)

df_clean["duration"] = df_clean["duration"].apply(
    lambda x: x.strftime("%H:%M:%S")
)

bookings["status"] = bookings["status"].fillna("Unknown")
bookings["status"] = bookings["status"].replace(
    "INVALID",
    "Unknown"
)

bookings["status_quality"] = bookings["status"].map({
    "Unknown": "Missing/Invalid",
    "CONFIRMED": "Valid",
    "CANCELLED": "Valid",
    "PENDING": "Valid"
})


passengers["last_name"] = (
    passengers["last_name"].fillna("Unknown")
)

passengers["last_name_quality"] = "Valid"

passengers.loc[
    passengers["last_name"] == "Unknown",
    "last_name_quality"
] = "Missing"

payments["amount"] = pd.to_numeric(
    payments["amount"].replace("INVALID", pd.NA),
    errors="coerce"
)

payments["amount_quality"] = (
    payments["amount"]
    .isna()
    .map({
        True: "Missing/Invalid",
        False: "Valid"
    })
)

df_clean.to_csv(
    "cleaned_data/flights_clean.csv",
    index=False
)

bookings.to_csv(
    "cleaned_data/bookings_clean.csv",
    index=False
)

passengers.to_csv(
    "cleaned_data/passengers_clean.csv",
    index=False
)

payments.to_csv(
    "cleaned_data/payments_clean.csv",
    index=False
)

engine = create_engine("sqlite:///airlines.db")

df_clean.to_sql(
    "flights",
    engine,
    if_exists="replace",
    index=False
)

bookings.to_sql(
    "bookings",
    engine,
    if_exists="replace",
    index=False
)

passengers.to_sql(
    "passengers",
    engine,
    if_exists="replace",
    index=False
)

payments.to_sql(
    "payments",
    engine,
    if_exists="replace",
    index=False
)

with engine.begin() as conn:

    conn.execute(text(
        "DROP TABLE IF EXISTS dim_passenger"
    ))

    conn.execute(text("""
        CREATE TABLE dim_passenger AS
        SELECT
            passenger_id,
            age,
            gender
        FROM passengers
    """))

    conn.execute(text(
        "DROP TABLE IF EXISTS dim_flight"
    ))

    conn.execute(text("""
        CREATE TABLE dim_flight AS
        SELECT
            flight_id,
            airline,
            source,
            destination,
            departure_time,
            arrival_time,
            duration,
            overnight,
            time_quality,
            duration_mismatch,
            overall_quality,
            flight_id_valid,
            duplicate_flight_id
        FROM flights
    """))

    conn.execute(text(
        "DROP TABLE IF EXISTS fact_booking"
    ))

    conn.execute(text("""
        CREATE TABLE fact_booking AS
        SELECT
            booking_id,
            passenger_id,
            flight_id,
            booking_date,
            status,
            status_quality
        FROM bookings
    """))

    conn.execute(text(
        "DROP TABLE IF EXISTS fact_payment"
    ))

    conn.execute(text("""
        CREATE TABLE fact_payment AS
        SELECT
            payment_id,
            booking_id,
            amount,
            payment_method,
            amount_quality
        FROM payments
    """))

print("Star schema created successfully!")

booking_trend = pd.read_sql("""
SELECT
    DATE(booking_date) AS booking_date,
    COUNT(*) AS total_bookings,
    SUM(
        CASE WHEN status = 'CONFIRMED'
        THEN 1 ELSE 0 END
    ) AS confirmed,
    SUM(
        CASE WHEN status = 'CANCELLED'
        THEN 1 ELSE 0 END
    ) AS cancelled,
    SUM(
        CASE WHEN status = 'PENDING'
        THEN 1 ELSE 0 END
    ) AS pending
FROM fact_booking
GROUP BY DATE(booking_date)
ORDER BY DATE(booking_date)
""", engine)

booking_trend.to_csv(
    "cleaned_data/booking_trend.csv",
    index=False
)

airline_performance = pd.read_sql("""
SELECT
    airline,
    COUNT(*) AS total_flights,
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
ORDER BY total_flights DESC
""", engine)

airline_performance.to_csv(
    "cleaned_data/airline_performance.csv",
    index=False
)


route_performance = pd.read_sql("""
SELECT
    source,
    destination,
    COUNT(*) AS total_flights
FROM dim_flight
WHERE overall_quality = 'Valid'
GROUP BY source, destination
ORDER BY total_flights DESC
LIMIT 10
""", engine)

route_performance.to_csv(
    "cleaned_data/route_performance.csv",
    index=False
)


booking_status = pd.read_sql("""
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
ORDER BY bookings DESC
""", engine)

booking_status.to_csv(
    "cleaned_data/booking_status.csv",
    index=False
)


data_quality = pd.read_sql("""
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
FROM fact_payment
""", engine)

data_quality.to_csv(
    "cleaned_data/data_quality.csv",
    index=False
)

print("All pipeline outputs created successfully!")

print("\nFinal row counts:")

print(
    "Flights:",
    len(df_clean)
)

print(
    "Bookings:",
    len(bookings)
)

print(
    "Passengers:",
    len(passengers)
)

print(
    "Payments:",
    len(payments)
)

print("\nPipeline completed successfully!")