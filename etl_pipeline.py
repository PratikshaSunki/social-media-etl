import os
import logging
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load credentials from .env
load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "social_media_dw")

DB_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
CSV_FILE_PATH = os.path.join("data", "Time-Wasters on Social Media.csv")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def extract(file_path: str) -> pd.DataFrame:
    logging.info("Starting Data Extraction...")
    df = pd.read_csv(file_path)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )
    logging.info("Extracted %d records successfully.", len(df))
    return df

def transform(df: pd.DataFrame):
    logging.info("Transforming raw data into Dimensional Models...")
    
    # Fix: reset the index after dropna so activity_id has no gaps
    df = df.dropna(subset=["userid"]).copy().reset_index(drop=True)
    df["userid"] = df["userid"].astype(int)
    
    dim_users = df[[
        "userid", "age", "gender", "location", "profession", 
        "demographics", "platform", "devicetype", "os", "connectiontype"
    ]].drop_duplicates(subset=["userid"]).copy()

    fact_activity = df[[
        "userid", "video_id", "video_category", "video_length", 
        "total_time_spent", "number_of_sessions", "engagement", 
        "time_spent_on_video", "number_of_videos_watched", 
        "scroll_rate", "productivityloss", "satisfaction", 
        "addiction_level", "watch_reason"
    ]].copy()

    fact_activity.reset_index(inplace=True)
    fact_activity.rename(columns={"index": "activity_id"}, inplace=True)
    fact_activity["activity_id"] += 1

    logging.info("Transformation finished: %d dim records, %d fact records.", len(dim_users), len(fact_activity))
    return dim_users, fact_activity

def load(dim_users: pd.DataFrame, fact_activity: pd.DataFrame, db_uri: str):
    logging.info("Loading records into PostgreSQL Data Mart...")
    engine = create_engine(db_uri)

    # One transaction: if anything fails, nothing is changed in the database
    with engine.begin() as conn:
        # Drop the fact table first because it depends on the dimension table
        conn.execute(text("DROP TABLE IF EXISTS fact_activity"))
        conn.execute(text("DROP TABLE IF EXISTS dim_users"))

        dim_users.to_sql("dim_users", con=conn, index=False)
        fact_activity.to_sql("fact_activity", con=conn, index=False)

        # Add the keys that make this a real star schema
        conn.execute(text("ALTER TABLE dim_users ADD PRIMARY KEY (userid)"))
        conn.execute(text("ALTER TABLE fact_activity ADD PRIMARY KEY (activity_id)"))
        conn.execute(text(
            "ALTER TABLE fact_activity "
            "ADD CONSTRAINT fk_fact_activity_user "
            "FOREIGN KEY (userid) REFERENCES dim_users (userid)"
        ))
    
    logging.info("ETL Pipeline completed successfully! Records loaded into PostgreSQL.")

if __name__ == "__main__":
    raw_df = extract(CSV_FILE_PATH)
    dim_u, fact_a = transform(raw_df)
    load(dim_u, fact_a, DB_URI)