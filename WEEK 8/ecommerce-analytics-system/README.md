# E-Commerce Analytics System

## Overview

This project is an end-to-end Data Engineering mini project that simulates an e-commerce analytics pipeline using Python, Pandas, SQLite, and SQL.

The system generates realistic datasets with intentional inconsistencies, cleans the data, loads it into a relational database, performs advanced SQL analytics, and provides a command-line reporting tool.

---

## Project Architecture

Raw Data Generation
        ↓
Data Cleaning (Pandas)
        ↓
SQLite Database
        ↓
SQL Analytics
        ↓
CLI Reporting Tool

---

## Technologies Used

- Python 3
- Pandas
- Faker
- SQLite
- SQL
- argparse

---

## Project Structure

```
ecommerce-analytics-system
│
├── data
│   ├── raw
│   └── cleaned
│
├── scripts
│   ├── generate_data.py
│   ├── clean_data.py
│   ├── load_database.py
│   ├── run_sql_reports.py
│   ├── report_cli.py
│   └── test_edge_cases.py
│
├── sql
│   ├── schema.sql
│   ├── aggregations.sql
│   ├── window_functions.sql
│   └── cohort_analysis.sql
│
├── database
│
├── output
│
├── screenshots
│
└── README.md
```

---

## Features

### Data Generation

- Generate Customers
- Generate Products
- Generate Orders
- Generate Order Items

Intentional issues generated:

- Invalid Emails
- NULL Customer IDs
- Mixed Date Formats
- Negative Quantities
- Messy Product Names

---

### Data Cleaning

- Remove duplicates
- Handle NULL values
- Standardize dates
- Validate email format
- Normalize product names
- Validate referential integrity

---

### Database

SQLite database with

- Primary Keys
- Foreign Keys
- CHECK Constraints
- NOT NULL Constraints

---

### SQL Analytics

Implemented:

- Revenue Analysis
- Customer Analytics
- Product Analytics
- Monthly Revenue
- Return Analysis
- Running Totals
- Moving Average
- Customer Ranking
- Cohort Analysis
- Retention Analysis
- Churn Analysis
- RFM Segmentation

---

### CLI Reporting Tool

Available reports

```
python scripts/report_cli.py --report revenue

python scripts/report_cli.py --report top_customers

python scripts/report_cli.py --report monthly

python scripts/report_cli.py --report retention

python scripts/report_cli.py --report segments

python scripts/report_cli.py --report returns
```

---

## Edge Cases Tested

- Zero Orders
- Single Customer
- Future Dates
- Invalid Foreign Keys
- Empty Result Sets

---

## How to Run

Generate Data

```
python scripts/generate_data.py
```

Clean Data

```
python scripts/clean_data.py
```

Load Database

```
python scripts/load_database.py
```

Run SQL Reports

```
python scripts/run_sql_reports.py
```

Run CLI

```
python scripts/report_cli.py --report revenue
```

Run Edge Case Tests

```
python scripts/test_edge_cases.py
```

---

## Learning Outcomes

This project demonstrates

- Data Generation
- Data Cleaning
- ETL Pipeline
- SQL Analytics
- Window Functions
- CTEs
- SQLite
- Command Line Applications
- Data Validation
- Customer Analytics