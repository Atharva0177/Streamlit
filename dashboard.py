import streamlit as st
import pandas as pd

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
        
        # Reorder columns
        columns_order = ['video_id','nature_crime','latitude','risk_percentage','timestamp', 'status','disapprove_reason']  # Specify the desired column order
        df = df[columns_order]
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def generate_graph(df, plot_style, x_column, y_column, color_column=None):
    if not df.empty:
        st.write("### Real-time Data Visualization")
        
        if plot_style == 'line':
            # Line plot
            fig = px.line(df, x=x_column, y=y_column, color=color_column, line_dash=color_column,
                          title="Line Plot")
        elif plot_style == 'bar':
            # Bar plot
            if color_column:
                fig = px.bar(df, x=x_column, y=y_column, color=x_column, title="Bar Plot")
            else:
                fig = px.bar(df, x=x_column, y=y_column, title="Bar Plot")
            fig.update_layout(xaxis_title=x_column.capitalize(), yaxis_title=y_column.capitalize())  # Update x-axis and y-axis titles
        elif plot_style == 'pie':
            # Pie chart
            fig = px.pie(df, values=y_column, names=x_column, title='Pie Chart')
        elif plot_style == 'histogram':
            # Histogram
            fig = px.histogram(df, x=y_column, color=color_column, title='Histogram')
            fig.update_layout(xaxis_title=x_column.capitalize(), yaxis_title="Count")  # Update x-axis and y-axis titles
        elif plot_style == 'crime_frequency':
            # Bar plot for crime frequency
            crime_frequency = df[x_column].value_counts().reset_index()
            crime_frequency.columns = [x_column, 'count']  # Rename columns for clarity
            if color_column:
                fig = px.bar(crime_frequency, x=x_column, y='count', color=x_column, title='Frequency of Crime Types')
            else:
                fig = px.bar(crime_frequency, x=x_column, y='count', title='Frequency of Crime Types')
            fig.update_layout(xaxis_title=x_column.capitalize(), yaxis_title="Frequency")  # Update x-axis and y-axis titles
        
        st.plotly_chart(fig)




def main():
    st.title("Real-time Data Visualization Dashboard")
    st.write("This dashboard visualizes real-time data from DynamoDB.")
    
    # Load data initially
    df = load_data()
    
    # Sidebar for customization options
    st.sidebar.title("Customization Options")
    plot_style = st.sidebar.radio("Plot Style:", ['line', 'bar', 'pie', 'histogram', 'crime_frequency'])
    x_column = st.sidebar.selectbox("X-axis:", df.columns)
    y_column = st.sidebar.selectbox("Y-axis:", df.columns)
    color_column = st.sidebar.selectbox("Color By:", [None] + list(df.columns))
    
    # Main content area
    st.header("Graph Visualization")
    st.write("Select the plot style and parameters from the sidebar to visualize the data.")
    generate_graph(df, plot_style, x_column, y_column, color_column)
    
    # Database view
    st.header("Entire Database")
    st.write("View the entire database as an Excel sheet.")
    
    st.dataframe(df)
    
    # Button to manually refresh the graph and database view
    if st.button("Refresh"):
        st.rerun()  # Refresh the page to display updated graph and database view

if __name__ == "__main__":
    main()
