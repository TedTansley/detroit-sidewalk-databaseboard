import sqlite3
import pandas as pd
import os

DB_PATH = "sidewalk_data.sqlite"
CSV_MANUAL_LATLONG_PATH = "manual_latlong.csv"

def update_parcel_with_manual_latlong():
    # Ensure connection is created at the start
    try:
        conn = sqlite3.connect(DB_PATH)
    except Exception as e:
        print(f"❌ Error connecting to the database: {e}")
        return  # Stop execution if connection fails

    try:
        # Load parcels and sidewalk reports from database
        parcel_df = pd.read_sql_query("SELECT * FROM parcels", conn)
        sidewalk_df = pd.read_sql_query("SELECT * FROM sidewalk_reports", conn)

        # Load and merge manual latitude/longitude data
        if os.path.exists(CSV_MANUAL_LATLONG_PATH):
            manual_latlong_df = pd.read_csv(CSV_MANUAL_LATLONG_PATH)
            parcel_df = pd.concat([parcel_df, manual_latlong_df], ignore_index=True)
        
        # Merge updated parcel data with sidewalk reports
        merged_df = sidewalk_df.merge(parcel_df, on="address", how="left")

        # Check if previous merged_parcel_sidewalk exists
        prev_df = pd.DataFrame()

        # Ensure connection is still valid
        if conn:
            table_check = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='merged_parcel_sidewalk';"
            ).fetchone()

            if table_check:
                prev_df = pd.read_sql_query("SELECT * FROM merged_parcel_sidewalk", conn)
            else:
                print("⚠️ No previous merged_parcel_sidewalk found. First-time run.")

        if not prev_df.empty:
            # Identify changes
            added_rows = merged_df[~merged_df["address"].isin(prev_df["address"])]
            removed_rows = prev_df[~prev_df["address"].isin(merged_df["address"])]
            modified_rows = merged_df.merge(prev_df, on="address", suffixes=("_new", "_old"))
            modified_rows = modified_rows[
                (modified_rows["latitude_new"] != modified_rows["latitude_old"]) |
                (modified_rows["longitude_new"] != modified_rows["longitude_old"])
            ]

            # Log changes
            changes_df = pd.concat([added_rows.assign(change_type="added"),
                                    removed_rows.assign(change_type="removed"),
                                    modified_rows.assign(change_type="modified")])
            changes_df["change_date"] = pd.Timestamp.today().date()
            changes_df.to_sql("merged_parcel_sidewalk_changes", conn, if_exists="append", index=False)

            # Replace previous version
            conn.execute("DROP TABLE IF EXISTS merged_parcel_sidewalk_previous")
            conn.execute("ALTER TABLE merged_parcel_sidewalk RENAME TO merged_parcel_sidewalk_previous")
            conn.commit()

        # Store the merged dataset in the database
        merged_df.to_sql("merged_parcel_sidewalk", conn, if_exists="replace", index=False)
        print("✅ Merged parcel and sidewalk data stored successfully.")

    except Exception as e:
        print(f"❌ Error during processing: {e}")

    finally:
        # Ensure the connection is closed properly
        if conn:
            conn.close()

if __name__ == "__main__":
    update_parcel_with_manual_latlong()
