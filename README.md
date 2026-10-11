# Social Media Usage ETL Pipeline

A small Python project that processes social media usage data from a CSV file, stores it in a SQLite database, and runs SQL queries to explore usage patterns.

## Technologies Used

- Python
- Pandas
- SQLAlchemy
- SQLite

## How It Works

1. **Extract:** Read the `Time-Wasters on Social Media.csv` dataset using Pandas and standardize column names.
2. **Transform:** Remove records without a user ID, convert user IDs to integers, and split the data into two tables:
   - `dim_users` — user details such as age, profession, and platform.
   - `fact_activity` — activity details such as time spent, video category, and addiction level.
3. **Load:** Save both tables to `social_media_dw.db` using SQLite.
4. **Analyze:** Run SQL queries to rank users by time spent within each platform and calculate average video watch time by category.

The sample dataset contains 1,000 records. In the current run, the pipeline created 1,000 user records and 1,000 activity records.


## How to Run

Install the required packages:

```bash
pip install pandas sqlalchemy
```

Run the ETL pipeline:

```bash
python etl_pipeline.py
```

Run the SQL analysis:

```bash
python run_analytics.py
```

## SQL Analysis

- **Platform-wise usage ranking:** Uses `JOIN` and `DENSE_RANK()` to rank users by total time spent within each platform.
- **Average watch time by category:** Uses `AVG() OVER (PARTITION BY ...)` to show each record alongside its video category's average watch time.

Results are printed in the terminal. The current queries display up to 15 rows each.

## Notes

This is a learning project focused on ETL, relational data modeling, and SQL window functions. Each ETL run replaces the existing SQLite tables rather than adding new records.
