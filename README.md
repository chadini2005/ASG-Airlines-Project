# Airline Data Engineering and Business Intelligence Analysis

## Project Overview

This project presents an end-to-end data engineering and business intelligence workflow for analyzing airline operational data.

The project uses an airline dataset containing information about flights, passengers, bookings, and payments. The raw Excel data was processed using Python and Pandas, cleaned and validated, stored in an SQLite database, and organized into a dimensional model for analytical processing.

SQL was used to perform business analysis and generate key performance indicators related to flights, bookings, airlines, routes, payments, and data quality. The processed datasets were prepared for visualization through Power BI.

## Project Objectives

- Extract airline data from the provided Excel workbook.
- Identify missing, duplicate, invalid, and inconsistent records.
- Clean and validate the data using Python and Pandas.
- Develop a reproducible data-processing pipeline.
- Store processed data in an SQLite database.
- Create a fact and dimension-based data model.
- Perform SQL-based business analysis.
- Generate key performance indicators.
- Analyze booking, flight, route, airline, and payment information.
- Present analytical results using Power BI.
- Protect sensitive passenger information from unnecessary exposure.

## Dataset

The original Excel workbook contains four datasets:

| Dataset | Records | Description |
|---|---:|---|
| Flights | 1,020 | Flight, airline, route and timing information |
| Bookings | 1,000 | Booking and booking-status information |
| Passengers | 1,039 | Passenger demographic and personal information |
| Payments | 1,000 | Payment transaction information |

## Data Preprocessing

The data was cleaned and validated using Python and Pandas.

The main preprocessing activities included:

- Removal of 15 exact duplicate flight records.
- Standardization of missing and `UNKNOWN` airline values.
- Validation of flight identifiers.
- Identification of duplicate flight IDs.
- Validation of departure and arrival timestamps.
- Identification of overnight flights.
- Detection of inconsistent flight timing and duration.
- Standardization of invalid or missing booking statuses.
- Conversion and validation of payment amounts.
- Handling of missing passenger last names.
- Creation of data-quality indicators.

The cleaned Flights dataset contains 1,005 records.

## Data Engineering Pipeline

The project follows the workflow:

Excel Dataset  
↓  
Python / Pandas  
↓  
Data Cleaning and Validation  
↓  
SQLite Database  
↓  
Star Schema  
↓  
SQL Analysis  
↓  
Power BI Dashboard

A Python pipeline script was developed to automate the major data-processing and database-generation steps.

## Database Design

The processed data is stored in an SQLite database named `airlines.db`.

The dimensional model consists of:

### Dimension Tables

- `dim_passenger`
- `dim_flight`

### Fact Tables

- `fact_booking`
- `fact_payment`

This structure separates descriptive information from transactional information and provides a suitable foundation for analytical queries and business intelligence reporting.

## SQL Analysis

SQL queries were used to generate analytical results including:

- Flight KPIs
- Booking KPIs
- Cancellation rate
- Airline performance
- Top routes
- Average flight duration
- Booking-status distribution
- Booking trends
- Payment statistics
- Payment-method analysis
- Data-quality summary

## Key Results

Some of the major results obtained from the analysis are:

- **Total flights after cleaning:** 1,005
- **Total bookings:** 1,000
- **Valid flight records:** 1,004
- **Flight anomalies:** 