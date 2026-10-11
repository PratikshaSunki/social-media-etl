import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

# Load credentials from .env
load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "social_media_dw")

DB_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def productivity_label(score: float) -> str:
    """Turn a 1-10 productivity-loss score into a readable label."""
    if score <= 3:
        return "Low"
    if score <= 6:
        return "Moderate"
    return "High"


def generate_dashboard():
    engine = create_engine(DB_URI)

    # 1. Platform Comparison
    q_platform = """
    SELECT 
        u.platform,
        ROUND(AVG(f.total_time_spent)::numeric, 1) as avg_time
    FROM fact_activity f
    JOIN dim_users u ON f.userid = u.userid
    GROUP BY u.platform
    ORDER BY avg_time DESC;
    """
    df_platform = pd.read_sql_query(q_platform, engine)

    # 2. Category Benchmark (GROUP BY instead of DISTINCT + window function)
    q_category = """
    SELECT 
        video_category,
        ROUND(AVG(time_spent_on_video)::numeric, 1) as avg_watch_time
    FROM fact_activity
    GROUP BY video_category
    ORDER BY avg_watch_time DESC
    LIMIT 6;
    """
    df_category = pd.read_sql_query(q_category, engine)

    # 3. Overall Totals
    q_kpi = """
    SELECT 
        COUNT(DISTINCT u.userid) as total_users,
        ROUND(AVG(f.productivityloss)::numeric, 0) as avg_prod_loss,
        ROUND(AVG(f.total_time_spent)::numeric, 0) as avg_overall_time
    FROM fact_activity f
    JOIN dim_users u ON f.userid = u.userid;
    """
    df_kpi = pd.read_sql_query(q_kpi, engine)

    # Values computed from the data (no hardcoded text)
    total_users = int(df_kpi["total_users"].iloc[0])
    avg_minutes = int(df_kpi["avg_overall_time"].iloc[0])
    avg_hours = avg_minutes / 60
    prod_loss = int(df_kpi["avg_prod_loss"].iloc[0])

    # Dashboard styling
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig = plt.figure(figsize=(14, 8), facecolor="#F8FAFC")
    gs = fig.add_gridspec(3, 2, height_ratios=[0.5, 1.2, 1.2], hspace=0.35, wspace=0.25)

    ax_kpi = fig.add_subplot(gs[0, :])
    ax_kpi.axis("off")
    ax_kpi.text(0.0, 0.8, "Social Media Habits: What Takes Up People's Time?", fontsize=18, fontweight="bold", color="#0F172A")
    ax_kpi.text(0.0, 0.45, "PostgreSQL Data Mart Analytics & Behavior Metrics", fontsize=11, color="#64748B")

    cards = [
        f"People Surveyed: {total_users:,}",
        f"Daily Screen Time: {avg_minutes} mins (~{avg_hours:.1f} hrs)",
        f"Work Time Lost: {prod_loss} / 10 ({productivity_label(prod_loss)})",
    ]
    for i, card in enumerate(cards):
        ax_kpi.text(
            0.42 + (i * 0.2), 0.55, card,
            fontsize=10, fontweight="bold", color="#1E293B",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#E2E8F0", edgecolor="#CBD5E1")
        )

    # Platform Averages
    ax1 = fig.add_subplot(gs[1:, 0])
    bars1 = ax1.bar(df_platform["platform"], df_platform["avg_time"], color="#3B82F6", width=0.55)
    ax1.set_title("Which App Takes the Most Time Daily?", fontsize=12, fontweight="bold", color="#1E293B", pad=12)
    ax1.set_ylabel("Minutes Spent per Day", fontsize=10, color="#475569")
    ax1.grid(axis="y", linestyle="--", alpha=0.5)
    ax1.set_facecolor("#FFFFFF")
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, yval + 2, f"{yval}m", ha="center", fontsize=9, fontweight="bold", color="#334155")

    # Category Benchmarks
    ax2 = fig.add_subplot(gs[1:, 1])
    bars2 = ax2.barh(df_category["video_category"], df_category["avg_watch_time"], color="#10B981", height=0.55)
    ax2.set_title("Which Videos Keep People Watching the Longest?", fontsize=12, fontweight="bold", color="#1E293B", pad=12)
    ax2.set_xlabel("Minutes Spent per Single Video", fontsize=10, color="#475569")
    ax2.grid(axis="x", linestyle="--", alpha=0.5)
    ax2.invert_yaxis()
    ax2.set_facecolor("#FFFFFF")
    for bar in bars2:
        xval = bar.get_width()
        ax2.text(xval + 0.2, bar.get_y() + bar.get_height() / 2, f"{xval}m", va="center", fontsize=9, fontweight="bold", color="#334155")

    output_filename = "dashboard.png"
    plt.savefig(output_filename, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"\n[SUCCESS] Dashboard generated safely: {output_filename}")

if __name__ == "__main__":
    generate_dashboard()