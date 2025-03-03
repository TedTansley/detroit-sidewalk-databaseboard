import sqlite3 
import pandas as pd
import os

DB_PATH = "sidewalk_data.sqlite"
CSV_MANUAL_LATLONG_PATH = "manual_latlong.csv"

def update_parcel_with_manual_latlong():
    try:
        conn = sqlite3.connect(DB_PATH)
        parcel_df = pd.read_sql_query("SELECT * FROM parcels", conn)
        sidewalk_df = pd.read_sql_query("SELECT * FROM sidewalk_reports", conn)
        
        if os.path.exists(CSV_MANUAL_LATLONG_PATH):
            manual_latlong_df = pd.read_csv(CSV_MANUAL_LATLONG_PATH)
            parcel_df = pd.concat([parcel_df, manual_latlong_df], ignore_index=True)
        
        merged_df = sidewalk_df.merge(parcel_df, on="address", how="left")
        
        prev_df = pd.read_sql_query("SELECT * FROM merged_parcel_sidewalk", conn) if conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='merged_parcel_sidewalk';"
        ).fetchone() else pd.DataFrame()
        
        if not prev_df.empty:
            changes_df = pd.DataFrame()
            
            added_rows = merged_df[~merged_df["address"].isin(prev_df["address"])]
            removed_rows = prev_df[~prev_df["address"].isin(merged_df["address"])]
            modified_rows = merged_df.merge(prev_df, on="address", suffixes=("_new", "_old"))
            modified_rows = modified_rows[
                (modified_rows["latitude_new"] != modified_rows["latitude_old"]) |
                (modified_rows["longitude_new"] != modified_rows["longitude_old"])
            ]
            
            if not added_rows.empty:
                added_rows["change_type"] = "added"
                changes_df = pd.concat([changes_df, added_rows])
            if not removed_rows.empty:
                removed_rows["change_type"] = "removed"
                changes_df = pd.concat([changes_df, removed_rows])
            if not modified_rows.empty:
                modified_rows["change_type"] = "modified"
                changes_df = pd.concat([changes_df, modified_rows])
            
            if not changes_df.empty:
                changes_df["change_date"] = pd.Timestamp.today().date()
                changes_df.to_sql("merged_parcel_sidewalk_changes", conn, if_exists="append", index=False)

                
        merged_df.to_sql("merged_parcel_sidewalk", conn, if_exists="replace", index=False)
        print("✅ Merged data updated successfully.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_parcel_with_manual_latlong()
