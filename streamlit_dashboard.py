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
