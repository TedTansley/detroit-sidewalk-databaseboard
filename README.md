# City of Detroit Sidewalk Reporting Database & Dashboard
Repository to store and visualize the Detroit sidewalk data from their ArcGIS server. 


## Initial Run: 
- Storing parcel data I previously cleaned up that is from 2018 into my SQL database, sidewalk_data.sqlite.

## Weekly Run:
- Running fetch_sidewalk.py to grab the reports from the GIS server and storing it into the SQL database.
- Running update_latlong_store_old.py to:
  - Merge parcel data with a csv doc that has latitude/longitude data for addresses not in the parcel data
  - Merge parcel data with sidewalk report data
  - Stores previously stored merged data into a new table
  - Checks differences between recently stored and previously stored.
  - Stores the differences into a new SQL table
