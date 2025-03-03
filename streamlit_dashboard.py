import streamlit as st
import streamlit as st
import dash_setup  # Import your module
from streamlit_folium import folium_static  # For displaying folium maps

# Page title
st.title("Sidewalk Damage Reports Dashboard")

# Load data (assuming the database connection is handled in dash_setup)
df = dash_setup.df  

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Charts", "Map"])

# Home Page
if page == "Home":
    st.write("Welcome to the Sidewalk Damage Reports Dashboard!")

# Charts Page
elif page == "Charts":
    st.subheader("Charts")

    # Plot Creation Year Chart
    st.write("### Reports per Creation Year")
    fig1 = dash_setup.plot_creation_year(df)
    st.pyplot(fig1)

    # Plot Cumulative Reports Chart
    st.write("### Cumulative Reports Over Time")
    fig2 = dash_setup.plot_cumulative_plot(df)
    st.pyplot(fig2)

# Map Page
elif page == "Map":
    st.subheader("Map of Sidewalk Issues")
    
    # Generate Folium map
    folium_map = dash_setup.map_sidewalk_data(df)
    
    # Display Folium map in Streamlit
    folium_static(folium_map)


# Change Log
elif page == "Change Log":
    st.subheader("Sidewalk Issues Change Log")
    db_path = "sidewalk_data.sqlite"  
    # Date filters
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    # Convert dates to string format for filtering
    start_date = start_date.strftime("%Y-%m-%d") if start_date else None
    end_date = end_date.strftime("%Y-%m-%d") if end_date else None
    # Fetch and display the change log
    df = dash_setup.get_change_log(db_path, start_date, end_date)
    
    if df.empty:
         st.warning("No changes found for the selected date range.")
    else:
         st.dataframe(df)
