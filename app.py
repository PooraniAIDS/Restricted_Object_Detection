import os
import sqlite3
import pandas as pd
import streamlit as st
from src.database import init_db, set_restricted_categories, get_restricted_categories

st.set_page_config(page_title="AI Security Command Center", layout="wide")

# Ensure DB schema & tables are initialized on startup
init_db()

st.title("🛡️ AI Security Command & Restricted Object System")

DB_PATH = os.path.abspath("logs/restricted_objects.db")

# Sidebar - Restriction Rules Control Panel
st.sidebar.header("⚙️ Restriction Rules Config")

available_items = [
    "knife", "cell phone", "scissors", "pistol", "handgun", 
    "bottle", "remote", "cup", "mouse", "keyboard", "person"
]
current_restricted = get_restricted_categories()

selected_restricted = st.sidebar.multiselect(
    "Select Items to Mark as RESTRICTED:",
    options=available_items,
    default=[item for item in current_restricted if item in available_items] or ["knife", "cell phone"]
)

if st.sidebar.button("Update Restricted Rules"):
    set_restricted_categories(selected_restricted)
    st.sidebar.success("Updated restriction rules!")

def load_data():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    
    conn = sqlite3.connect(DB_PATH)
    # Safely decode raw bytes to prevent UTF-8 Arrow/Pandas crashes
    conn.text_factory = lambda x: str(x, 'utf-8', 'ignore') if isinstance(x, bytes) else str(x)
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM detections ORDER BY id DESC")
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
    except Exception as e:
        st.error(f"Error reading database: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()

    if not df.empty:
        # Safe float conversion for confidence
        if "confidence" in df.columns:
            def clean_conf(val):
                try:
                    s = str(val).replace("%", "").strip()
                    return round(float(s), 2)
                except:
                    return 0.0
            df["confidence"] = df["confidence"].apply(clean_conf)

        # Standardize category string values
        if "category" in df.columns:
            df["category"] = df["category"].apply(lambda x: str(x).lower() if pd.notnull(x) else "unknown")

        # Standardize threat binary flag
        if "is_restricted" in df.columns:
            df["is_restricted"] = pd.to_numeric(df["is_restricted"], errors="coerce").fillna(0).astype(int)

    return df

df = load_data()

# Top Analytical Metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Objects Logged", value=len(df))

with col2:
    if not df.empty and "is_restricted" in df.columns:
        restricted_count = int((df["is_restricted"] == 1).sum())
    else:
        restricted_count = 0
    st.metric(label="⚠️ Restricted Threats Detected", value=restricted_count)

with col3:
    st.metric(label="Active Restricted Rules", value=len(selected_restricted))

st.divider()

# Real-time Table & Charts Section
st.subheader("🚨 Real-Time Security Audit Log")

if not df.empty:
    st.dataframe(df, use_container_width=True)
    
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.subheader("📊 Detected Categories")
        st.bar_chart(df["category"].value_counts())
        
    with col_chart2:
        st.subheader("⚠️ Threat vs Normal Breakdown")
        if "is_restricted" in df.columns:
            threat_counts = df["is_restricted"].map({1: "Restricted Threat", 0: "Normal Item"}).value_counts()
            st.bar_chart(threat_counts)
        else:
            st.info("Run camera stream once to initialize threat analytics.")
else:
    st.warning("No logs in database. Run `python src/counting.py` in terminal!")

if st.button("Refresh Feed"):
    st.rerun()