import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="Data Visualization Demo",
    layout="wide"
)

# App title and description
st.title("Data Visualization Demo")
st.markdown("This demo app showcases a line chart for time series data and a donut chart for categorical data.")

# Generate random time series data
def generate_time_series():
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
    
    np.random.seed(42)  # For reproducibility
    data = {
        'Date': dates,
        'Sales': np.random.randint(100, 500, size=30),
        'Visits': np.random.randint(500, 1500, size=30),
        'Conversions': np.random.randint(50, 200, size=30)
    }
    return pd.DataFrame(data)

# Generate random categorical data
def generate_categorical_data():
    categories = ['Electronics', 'Clothing', 'Home & Kitchen', 'Books', 'Sports']
    np.random.seed(42)  # For reproducibility
    data = {
        'Category': categories,
        'Revenue': np.random.randint(10000, 50000, size=5)
    }
    return pd.DataFrame(data)

# Generate the data
time_series_df = generate_time_series()
categorical_df = generate_categorical_data()

# Create two columns for the charts
col1, col2 = st.columns(2)

# Line chart in the first column
with col1:
    st.subheader("Trend Analysis Over Time")
    
    # Metric selector
    metric = st.selectbox("Select Metric", ['Sales', 'Visits', 'Conversions'])
    
    # Create line chart with Plotly
    fig_line = px.line(
        time_series_df, 
        x='Date', 
        y=metric,
        title=f'{metric} Over Time',
        markers=True
    )
    
    fig_line.update_layout(
        xaxis_title='Date',
        yaxis_title=metric,
        height=400
    )
    
    st.plotly_chart(fig_line, use_container_width=True)

# Donut chart in the second column
with col2:
    st.subheader("Revenue by Category")
    
    # Create donut chart with Plotly
    fig_donut = px.pie(
        categorical_df,
        values='Revenue',
        names='Category',
        title='Revenue Distribution by Category',
        hole=0.4
    )
    
    fig_donut.update_layout(height=400)
    
    st.plotly_chart(fig_donut, use_container_width=True)

# Data tables
st.subheader("Raw Data")
tab1, tab2 = st.tabs(["Time Series Data", "Categorical Data"])

with tab1:
    st.dataframe(time_series_df)

with tab2:
    st.dataframe(categorical_df)

# Add an interactive element with a slider
st.subheader("Interactive Data Exploration")
days_to_show = st.slider("Number of days to display", 5, 30, 15)
filtered_df = time_series_df.iloc[-days_to_show:]

fig_filtered = px.line(
    filtered_df,
    x='Date',
    y=['Sales', 'Visits', 'Conversions'],
    title=f'Last {days_to_show} Days Metrics Comparison'
)

st.plotly_chart(fig_filtered, use_container_width=True)
