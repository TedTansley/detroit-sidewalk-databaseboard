import sqlite3
import pandas as pd
import os

DB_PATH = "sidewalk_data.sqlite"
CSV_MANUAL_LATLONG_PATH = "manual_latlong.csv"

def update_parcel_with_manual_latlong():
    try:
        # Establish connection to the database
        conn = sqlite3.connect(DB_PATH)
        
        # Read the current tables into pandas dataframes
        parcel_df = pd.read_sql_query("SELECT * FROM parcels", conn)
        sidewalk_df = pd.read_sql_query("SELECT * FROM sidewalk_reports", conn)
        
        # If the manual lat-long file exists, read it and append it to the parcel dataframe
        if os.path.exists(CSV_MANUAL_LATLONG_PATH):
            manual_latlong_df = pd.read_csv(CSV_MANUAL_LATLONG_PATH)
            parcel_df = pd.concat([parcel_df, manual_latlong_df], ignore_index=True)
        
        # Merge the two dataframes on the address column
        merged_df = sidewalk_df.merge(parcel_df, on="address", how="left")
        
        # Check if the merged_parcel_sidewalk table exists, and load it if it does
        prev_df = pd.read_sql_query("SELECT * FROM merged_parcel_sidewalk", conn) if conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='merged_parcel_sidewalk';"
        ).fetchone() else pd.DataFrame()
        
        # Initialize changes dataframe to store new and removed rows
        changes_df = pd.DataFrame()

        # If prev_df is not empty, compare it to merged_df to find new and removed rows
        if not prev_df.empty:
            # Find added rows: Rows in merged_df not in prev_df
            added_rows = merged_df[~merged_df["address"].isin(prev_df["address"])]
            if not added_rows.empty:
                added_rows["change_type"] = "added"
                changes_df = pd.concat([changes_df, added_rows])

            # Find removed rows: Rows in prev_df not in merged_df
            removed_rows = prev_df[~prev_df["address"].isin(merged_df["address"])]
            if not removed_rows.empty:
                removed_rows["change_type"] = "removed"
                changes_df = pd.concat([changes_df, removed_rows])

            # If there are any changes, log them into the changes table
            if not changes_df.empty:
                changes_df["change_date"] = pd.Timestamp.today().date()
                changes_df.to_sql("merged_parcel_sidewalk_changes", conn, if_exists="append", index=False)
        
        # Replace the merged_parcel_sidewalk table with the latest merged data (merged_df)
        merged_df.to_sql("merged_parcel_sidewalk", conn, if_exists="replace", index=False)

        print("✅ Merged data updated successfully.")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Close the database connection
        conn.close()

if __name__ == "__main__":
    update_parcel_with_manual_latlong()

