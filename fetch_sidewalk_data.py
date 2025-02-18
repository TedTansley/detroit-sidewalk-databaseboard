import requests
import sqlite3
import pandas as pd

# ArcGIS REST API Endpoint
ARCGIS_URL = "https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/Sidewalk_Reporter_Issues(public)/FeatureServer/0/query"

# Database Path
DB_PATH = "sidewalk_data.sqlite"

def fetch_sidewalk_data():
    """Fetch sidewalk data from ArcGIS REST API and return as a DataFrame."""
    params = {
        "f": "json",
        "where": "1=1",
        "returnGeometry": "true",
        "spatialRel": "esriSpatialRelIntersects",
        "geometryType": "esriGeometryEnvelope",
        "geometry": None,  # Specify geometry if needed
        "inSR": "102100",
        "outFields": "*",  # Fetch all fields
        "orderByFields": "objectid ASC",
        "outSR": "102100",
        "resultRecordCount": 1000,  # Records per request
    }
    all_data = []
    offset = 0

    # Loop to fetch data and handle pagination
    while True:
        params["resultOffset"] = offset
        response = requests.get(ARCGIS_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            if "features" in data and len(data["features"]) > 0:
                for feature in data["features"]:
                    attributes = feature["attributes"]
                    all_data.append(attributes)
                offset += len(data["features"])  # Increment offset
            else:
                break  # No more records
        else:
            print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
            break

    return pd.DataFrame(all_data)

def store_sidewalk_data(df):
    """Store sidewalk data in the SQLite database."""
    conn = sqlite3.connect(DB_PATH)

    df.to_sql("sidewalk_reports", conn, if_exists="replace", index=False)

    conn.close()
    print("✅ Sidewalk data fetched and stored successfully.")


#Make modifications to the dataframe and send dataframe to sqlite database
if __name__ == "__main__":
    sidewalk_df = fetch_sidewalk_data()
    print(sidewalk_df.columns)

    #drop values I'm not using
    sidewalk_df.drop(columns=['globalid', 'Report_ID'], inplace=True)

    # Convert the 'CreationDate' (which is in milliseconds) to a datetime format
    sidewalk_df['CreationDate'] = pd.to_datetime(sidewalk_df['CreationDate'], unit='ms', errors='coerce')

    # Extract additional information from 'CreationDate'
    sidewalk_df['creation_year'] = sidewalk_df['CreationDate'].dt.year
    sidewalk_df['creation_month'] = sidewalk_df['CreationDate'].dt.month
    sidewalk_df['creation_day'] = sidewalk_df['CreationDate'].dt.day
    sidewalk_df['creation_weekday'] = sidewalk_df['CreationDate'].dt.weekday  # 0=Monday, 6=Sunday
    sidewalk_df['creation_hour'] = sidewalk_df['CreationDate'].dt.hour
    sidewalk_df['creation_minute'] = sidewalk_df['CreationDate'].dt.minute

    #normalize values (make all lower case) update creationdate to creation_date
    sidewalk_df.rename(columns={'CreationDate': 'creation_date', 'Tree_Gaurantee': 'tree_guarantee'}, inplace=True)
    sidewalk_df['address'] = sidewalk_df['address'].str.lower()

    #address NaN values
    sidewalk_df.fillna({'tree_guarantee': 'none reported', 'inspect_date': 'none reported'}, inplace=True)

    store_sidewalk_data(sidewalk_df)

