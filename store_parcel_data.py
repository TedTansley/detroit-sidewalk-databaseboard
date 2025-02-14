import sqlite3
import pandas as pd
import os

CSV_PARCEL_PATH = "city_parcel_data_2018_cleaned.csv"
DB_PATH = "sidewalk_data.sqlite"

def load_parcel_data(csv_path):
    """Load fixed parcel data from CSV into a pandas DataFrame."""
    return pd.read_csv(csv_path)

def store_parcel_data_in_db(parcel_df):
    """Store parcel data in SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create the table with objectid as the primary key
    cur.execute("""
        CREATE TABLE IF NOT EXISTS parcels (
            objectid INTEGER PRIMARY KEY,
            parcelno TEXT,
            address TEXT,
            longitude REAL,
            latitude REAL,
            shape_area REAL
        )
    """)

    # Insert data into the database with conflict handling
    for _, row in parcel_df.iterrows():
        cur.execute("""
            INSERT INTO parcels (objectid, parcelno, address, longitude, latitude, shape_area)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(objectid) DO UPDATE SET
                parcelno=excluded.parcelno,
                address=excluded.address,
                longitude=excluded.longitude,
                latitude=excluded.latitude,
                shape_area=excluded.shape_area
        """, (row['objectid'], row['parcelno'], row['address'], row['longitude'], row['latitude'], row['shape_area']))

    # Commit and close the database connection
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Parcel data stored successfully.")

if __name__ == "__main__":
    if os.path.exists(CSV_PARCEL_PATH):
        parcel_df = load_parcel_data(CSV_PARCEL_PATH)
        store_parcel_data_in_db(parcel_df)
