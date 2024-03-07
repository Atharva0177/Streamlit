import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import boto3
import seaborn as sns
import plotly.express as px
import time

# Connect to DynamoDB
aws_access_key_id = "AKIA5FTZFJUJ6OFOAGUS"
aws_secret_access_key = "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"
aws_region = "us-east-2"
dynamodb_table_name = "envision"

dynamodb = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region)
table = dynamodb.Table(dynamodb_table_name)

@st.cache_data(ttl=10)  # Cache the data for 10 seconds
def load_data():
    try:
        response = table.scan()
        items = response.get('Items', [])
        df = pd.DataFrame(items)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def generate_graph(df, plot_style):
    if not df.empty:
        st.write("### Real-time Data Visualization")
        
        if plot_style == 'line':
            # Line plot
            fig = px.line(df, x='timestamp', y='risk_percentage', color='nature_crime', line_dash='nature_crime',
                          title="Risk Percentage Distribution by Crime Type")
        elif plot_style == 'bar':
            # Bar plot for risk percentage distribution by crime type
            fig = px.bar(df, x='timestamp', y='risk_percentage', color='nature_crime', title="Risk Percentage Distribution by Crime Type")
            fig.update_layout(xaxis_title="Timestamp", yaxis_title="Risk Percentage")  # Update x-axis and y-axis titles
        elif plot_style == 'pie':
            # Pie chart
            fig = px.pie(df, values='risk_percentage', names='nature_crime', title='Crime Type Distribution')
        elif plot_style == 'histogram':
            # Histogram
            fig = px.histogram(df, x='risk_percentage', color='nature_crime', title='Risk Percentage Distribution')
        elif plot_style == 'crime_frequency':
            # Bar plot for crime frequency
            crime_frequency = df['nature_crime'].value_counts().reset_index()
            crime_frequency.columns = ['nature_crime', 'count']  # Rename columns for clarity
            fig = px.bar(crime_frequency, x='nature_crime', y='count', color='nature_crime', title='Frequency of Crime Types')
            fig.update_layout(xaxis_title="Crime Type", yaxis_title="Frequency")  # Update x-axis and y-axis titles
        
        st.plotly_chart(fig)

def main():
    st.title("Real-time Data Visualization Dashboard")
    st.write("This dashboard visualizes real-time data from DynamoDB.")
    
    # Load data initially
    df = load_data()
    
    # Customization options
    plot_style = st.radio("Plot Style:", ['line', 'bar', 'pie', 'histogram', 'crime_frequency'])
    
    # Display the graph
    generate_graph(df, plot_style)
    
    # Button to manually refresh the graph
    if st.button("Refresh Graph"):
        st.experimental_rerun()  # Refresh the page to display updated graph

if __name__ == "__main__":
    main()