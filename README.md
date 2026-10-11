# Social Media Usage ETL Pipeline

A Python-based ETL project that processes social media usage data, stores it in PostgreSQL, and generates visualizations to analyze user activity and engagement patterns.


## Technologies Used

Python, Pandas, PostgreSQL, SQLAlchemy, Matplotlib

## Project Overview

- Extracted 1,000 social media usage records from a CSV dataset using Pandas.
- Cleaned and transformed the data into a star schema consisting of user dimension and activity fact tables.
- Loaded the transformed data into PostgreSQL with primary and foreign key constraints.
- Implemented transactional loading to support consistent and repeatable ETL execution.
- Performed SQL-based analysis using joins and aggregations to examine platform usage, video-watching patterns, and productivity loss.
- Generated a Matplotlib dashboard to visualize the analysis results.

## How to Run

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Configure PostgreSQL credentials in a `.env` file using `.env.example` as a reference.

Run the ETL pipeline:

```bash
python etl_pipeline.py
```

Generate the analytics dashboard:

```bash
python run_analytics.py
```