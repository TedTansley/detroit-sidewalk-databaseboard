import sqlite3
import os

DB_PATH = "sidewalk_data.sqlite"
conn = sqlite3.connect(DB_PATH)


import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd
import folium
from folium.plugins import FloatImage
from branca.element import MacroElement
from jinja2 import Template
from shapely.geometry import shape
from folium import FeatureGroup
from folium.map import MacroElement
import requests

df = pd.read_sql_query("SELECT * FROM merged_parcel_sidewalk", conn)


# Set font properties globally
#plt.rcParams['font.family'] = 'Montserrat'  # Choose your desired font family (e.g., 'Arial', 'Times New Roman', etc.)
#plt.rcParams['font.weight'] = 'bold'  # Set the font weight globally (optional)

def plot_creation_year(df):
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))  # Store the figure in a variable
    sns.set(style="whitegrid", rc={"axes.facecolor": "#F2F2F2", "figure.facecolor": "#9FD5B3"})
    
    # Create the bar plot
    ax = sns.countplot(x='creation_year', data=df, color='#004445')
    ax.set_title('Number of Open Sidewalk Damage Reports per Creation Year', size=20, color='#18252A')
    ax.set_xlabel('Creation Year', size=15, color='#18252A')
    ax.set_ylabel('Number of Reports', size=15, color='#18252A')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, color='#18252A')
    ax.tick_params(axis='y', colors='#18252A')

    # Add count labels on top of the bars
    for p in ax.patches:
        height = p.get_height()
        ax.text(p.get_x() + p.get_width() / 2, height - height * 0.1, int(height), 
                ha="center", va="center", color='#feb70d', fontsize=12)
    return fig


def plot_cumulative_plot(df):
    # Group data by creation year and compute cumulative sum
    reports_per_year = df.groupby('creation_year').size()
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot the cumulative sum as a line chart
    reports_per_year.cumsum().plot(kind='line', marker='o', color="#004445", ax=ax)

    # Set title and labels
    ax.set_title('Cumulative Number of Reports per Creation Year', size=20)
    ax.set_xlabel('Creation Year', size=15)
    ax.set_ylabel('Cumulative Number of Reports', size=15)
    ax.set_xticklabels(reports_per_year.index, rotation=45)
    ax.grid(True)  # Add gridlines for better readability

    return fig  # Return the figure object

def map_sidewalk_data(df):
    df['geometry'] = df.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)
    gdf_sidewalks = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")  # WGS 84 coordinate system
    gdf_sidewalks['creation_year'] = gdf_sidewalks['creation_year'].astype(str)
    # Create a Folium map centered at a Detroit location
    m = folium.Map(location=[42.363191, -83.092280], zoom_start=11.5)
    
    # Define style function for neighborhood GeoJSON
    def style_function(feature):
            color = "#F2F2F2"
            return {
                'fillColor': color,
                'color': 'black',  # Border color
                'weight': 1,       # Border width
                'fillOpacity': 0.3  # Opacity of the fill color
                }
    # Add the Detroit Neighborhoods GeoJSON as a layer
    url = "https://services2.arcgis.com/qvkbeam7Wirps6zC/ArcGIS/rest/services/Current_City_of_Detroit_Neighborhoods/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=geojson"
    response = requests.get(url)
    geojson_data = response.json()
    folium.GeoJson(
        geojson_data,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=['nhood_name']),
        name="Detroit Neighborhoods"
    ).add_to(m)
    # Define a dictionary for year-to-color mapping 
    color_mapping = {
        "2018": "#18252A",
        "2019": "#2e3761",
        "2020": "#94456C",
        "2021": "#5F355a",
        "2022": "#CB4D4F",
        "2023": "#F28E2B",
        "2024": "#607C97",
        "2025": "#279989"
    }
    # Create a feature group for each year
    year_groups = {year: FeatureGroup(name=f"Year {year}") for year in color_mapping.keys()}
    
    for idx, row in gdf_sidewalks.iterrows():
        color = color_mapping.get(row['creation_year'], "#279989")
        year_group = year_groups.get(str(row['creation_year']))
        if year_group:
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=3,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=1,
                popup=f"Creation Year: {row['creation_year']}<br>Address: {row['address']}"
                ).add_to(year_group)
    # Add each year group to the map
    for group in year_groups.values():
        group.add_to(m)
    # Add Layer Control for toggling layers
    folium.LayerControl().add_to(m)
    # Define the HTML for the color legend
    legend_html = """
    <div style="
        position: fixed;
        bottom: 50px;
        left: 50px;
        width: 200px;
        background-color: white;
        border: 2px solid grey;
        z-index: 1000;
        padding: 10px;
        border-radius: 8px;
        font-size: 12px;
        ">
        <b>Legend</b><br>
        <i style="background: #18252A; width: 12px; height: 12px; display: inline-block; margin-right: 5px;"></i> 2018<br>
        <i style="background: #2e3761; width: 12px; height: 12px; display: inline-block; margin-right: 5px;"></i> 2019<br>
        <i style="background: #94456C; width: 12px; height: 12px; display: inline-block; margin-right: 5px;"></i> 2020<br>
        <i style="background: #5F355a; width: 12px; height: 12px; display: inline-block; margin-right: 5px;"></i> 2021<br>
        <i style="background: #CB4D4F; width: 12px; height: 12px; display: inline-block; margin-right: 5px;"></i> 2022<br>
        <i style="background: #F28E2B; width: 12px; height: 12px; display: inline-block; margin-right: 5px;"></i> 2023<br>
        <i style="background: #607C97; width: 12px; height: 12px; display: inline-block; margin-right: 5px;"></i> 2024<br>
        <i style="background: #279989; width: 12px; height: 12px; display: inline-block; margin-right: 5px;"></i> 2025
    </div>
    """

    # Create a custom MacroElement to inject the legend
    class Legend(MacroElement):
        def __init__(self, legend_html):
            super().__init__()
            self._template = Template(f"""
                {{% macro html(this, kwargs) %}}
                {legend_html}
                {{% endmacro %}}
            """)

    # Add the legend to the map
    legend = Legend(legend_html)
    m.get_root().add_child(legend)

    # Display the map
    return m


def get_change_log(db_path, start_date=None, end_date=None):
    """
    Fetch change log data from the merged_parcel_sidewalk_changes table.
    Allows optional filtering by date range.
    """
    conn = sqlite3.connect(db_path)
    query = """
        SELECT * 
        FROM merged_parcel_sidewalk_changes
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Convert change_date to datetime for filtering
    df['change_date'] = pd.to_datetime(df['change_date'])
    
    if start_date:
        df = df[df['change_date'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['change_date'] <= pd.to_datetime(end_date)]
    
    return df
