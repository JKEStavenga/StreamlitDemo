import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="Exclusieve Schoenen Verkoop Dashboard",
    layout="wide"
)

# App title and description
st.title("Exclusieve Schoenen Verkoop Dashboard")
st.markdown("This dashboard visualizes shoe sales data across different locations and time periods.")

# Load data from CSV file
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("exclusieve_schoenen_verkoop_met_locatie.csv")
        # Check if date column exists and convert to datetime if needed
        date_columns = [col for col in df.columns if 'date' in col.lower() or 'datum' in col.lower()]
        if date_columns:
            # Assume the first match is our date column
            date_col = date_columns[0]
            df[date_col] = pd.to_datetime(df[date_col])
        return df
    except FileNotFoundError:
        st.error("File 'exclusieve_schoenen_verkoop_met_locatie.csv' not found. Please make sure the file exists in the same directory as this app.")
        # Return a sample dataframe to prevent errors
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Load the data
df = load_data()

# Check if dataframe is empty (file not found or other error)
if df.empty:
    st.warning("Using sample data since the CSV file couldn't be loaded.")
    # Create sample data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    locations = ['Amsterdam', 'Rotterdam', 'Utrecht', 'Den Haag', 'Eindhoven']
    shoe_types = ['Sneakers', 'Loafers', 'Boots', 'High Heels', 'Sandals']
    
    sample_data = []
    for _ in range(500):
        sample_data.append({
            'Datum': np.random.choice(dates),
            'Locatie': np.random.choice(locations),
            'SchoenType': np.random.choice(shoe_types),
            'Verkoop': np.random.randint(1, 10),
            'Prijs': np.random.randint(100, 500)
        })
    
    df = pd.DataFrame(sample_data)
else:
    # Display the first few rows and columns of the dataframe for verification
    st.subheader("Sample of loaded data")
    st.dataframe(df.head())
    
    # Identify key columns based on common naming patterns
    date_col = next((col for col in df.columns if 'date' in col.lower() or 'datum' in col.lower()), None)
    location_col = next((col for col in df.columns if 'location' in col.lower() or 'locatie' in col.lower()), None)
    product_col = next((col for col in df.columns if 'product' in col.lower() or 'schoen' in col.lower() or 'type' in col.lower()), None)
    sales_col = next((col for col in df.columns if 'sales' in col.lower() or 'verkoop' in col.lower()), None)
    price_col = next((col for col in df.columns if 'price' in col.lower() or 'prijs' in col.lower()), None)
    
    # If columns couldn't be identified, let the user select them
    if not all([date_col, location_col, sales_col]):
        st.warning("Could not automatically identify all required columns. Please select them below:")
        
        if not date_col:
            date_col = st.selectbox("Select date column:", df.columns)
        
        if not location_col:
            location_col = st.selectbox("Select location column:", df.columns)
        
        if not product_col:
            product_col = st.selectbox("Select product/shoe type column:", df.columns)
        
        if not sales_col:
            sales_col = st.selectbox("Select sales quantity column:", df.columns)
        
        if not price_col:
            price_col = st.selectbox("Select price column:", df.columns)

# Create a copy of the dataframe with consistent column names for easier processing
processed_df = df.copy()

# Rename columns to standardized names if we've identified them
column_mapping = {}
if 'date_col' in locals() and date_col:
    column_mapping[date_col] = 'Datum'
if 'location_col' in locals() and location_col:
    column_mapping[location_col] = 'Locatie'
if 'product_col' in locals() and product_col:
    column_mapping[product_col] = 'SchoenType'
if 'sales_col' in locals() and sales_col:
    column_mapping[sales_col] = 'Verkoop'
if 'price_col' in locals() and price_col:
    column_mapping[price_col] = 'Prijs'

if column_mapping:
    processed_df = processed_df.rename(columns=column_mapping)

# Ensure Datum is datetime
if 'Datum' in processed_df.columns:
    if not pd.api.types.is_datetime64_any_dtype(processed_df['Datum']):
        processed_df['Datum'] = pd.to_datetime(processed_df['Datum'], errors='coerce')

# Calculate revenue if we have sales and price
if 'Verkoop' in processed_df.columns and 'Prijs' in processed_df.columns:
    processed_df['Omzet'] = processed_df['Verkoop'] * processed_df['Prijs']

# Create two columns for the charts
col1, col2 = st.columns(2)

# Line chart in the first column - Time Series Analysis
with col1:
    st.subheader("Verkoop Trend Over Tijd")
    
    if 'Datum' in processed_df.columns:
        # Group by date and sum sales
        if 'Verkoop' in processed_df.columns:
            time_series = processed_df.groupby('Datum')['Verkoop'].sum().reset_index()
            
            # Create line chart with Plotly
            fig_line = px.line(
                time_series, 
                x='Datum', 
                y='Verkoop',
                title='Verkoop Trend',
                markers=True
            )
            
            fig_line.update_layout(
                xaxis_title='Datum',
                yaxis_title='Verkoop Aantal',
                height=400
            )
            
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("Sales quantity column not available for time series analysis.")
    else:
        st.warning("Date column not available for time series analysis.")

# Donut chart in the second column - Sales by Location
with col2:
    st.subheader("Verkoop per Locatie")
    
    if 'Locatie' in processed_df.columns and 'Verkoop' in processed_df.columns:
        # Group by location and sum sales
        location_sales = processed_df.groupby('Locatie')['Verkoop'].sum().reset_index()
        
        # Create donut chart with Plotly
        fig_donut = px.pie(
            location_sales,
            values='Verkoop',
            names='Locatie',
            title='Verkoop Distributie per Locatie',
            hole=0.4
        )
        
        fig_donut.update_layout(height=400)
        
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.warning("Location or sales quantity columns not available for donut chart.")

# Add additional visualizations based on available data
if 'SchoenType' in processed_df.columns and 'Verkoop' in processed_df.columns:
    st.subheader("Verkoop per Schoen Type")
    
    # Group by shoe type and sum sales
    shoe_type_sales = processed_df.groupby('SchoenType')['Verkoop'].sum().reset_index()
    
    # Create bar chart
    fig_bar = px.bar(
        shoe_type_sales,
        x='SchoenType',
        y='Verkoop',
        title='Verkoop per Schoen Type'
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

# Add filters based on available columns
st.sidebar.header("Filters")

# Date range filter
if 'Datum' in processed_df.columns:
    min_date = processed_df['Datum'].min().date()
    max_date = processed_df['Datum'].max().date()
    
    date_range = st.sidebar.date_input(
        "Selecteer Datum Bereik",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = processed_df[(processed_df['Datum'].dt.date >= start_date) & 
                                 (processed_df['Datum'].dt.date <= end_date)]
    else:
        filtered_df = processed_df
else:
    filtered_df = processed_df

# Location filter
if 'Locatie' in filtered_df.columns:
    all_locations = sorted(filtered_df['Locatie'].unique())
    selected_locations = st.sidebar.multiselect(
        "Selecteer Locaties",
        all_locations,
        default=all_locations
    )
    
    if selected_locations:
        filtered_df = filtered_df[filtered_df['Locatie'].isin(selected_locations)]

# Shoe type filter
if 'SchoenType' in filtered_df.columns:
    all_shoe_types = sorted(filtered_df['SchoenType'].unique())
    selected_shoe_types = st.sidebar.multiselect(
        "Selecteer Schoen Types",
        all_shoe_types,
        default=all_shoe_types
    )
    
    if selected_shoe_types:
        filtered_df = filtered_df[filtered_df['SchoenType'].isin(selected_shoe_types)]

# Display filtered data
st.subheader("Gefilterde Data")
st.dataframe(filtered_df)

# Add KPIs at the top if revenue data is available
if 'Verkoop' in processed_df.columns and 'Prijs' in processed_df.columns and 'Omzet' in processed_df.columns:
    st.subheader("Key Performance Indicators")
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        total_sales = filtered_df['Verkoop'].sum()
        st.metric("Totaal Verkoop", f"{total_sales}")
    
    with kpi2:
        total_revenue = filtered_df['Omzet'].sum()
        st.metric("Totaal Omzet", f"€{total_revenue:,.2f}")
    
    with kpi3:
        avg_price = filtered_df['Prijs'].mean()
        st.metric("Gemiddelde Prijs", f"€{avg_price:,.2f}")
    
    with kpi4:
        if 'Locatie' in filtered_df.columns:
            top_location = filtered_df.groupby('Locatie')['Verkoop'].sum().idxmax()
            st.metric("Top Locatie", f"{top_location}")
        elif 'SchoenType' in filtered_df.columns:
            top_shoe = filtered_df.groupby('SchoenType')['Verkoop'].sum().idxmax()
            st.metric("Top Schoen Type", f"{top_shoe}")
