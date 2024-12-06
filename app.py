import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Page config
st.set_page_config(page_title="Data Analysis Dashboard", layout="wide")

# File uploader
uploaded_file = st.file_uploader("Choose your Excel file", type=['xlsx', 'xls', 'csv'])

if uploaded_file is not None:
    try:
        # Read the data with explicit dtype handling
        if uploaded_file.name.endswith(('xlsx', 'xls')):
            # Read all sheets into a dictionary
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_names = excel_file.sheet_names
            
            # Display summary of all sheets
            st.subheader("Excel File Overview")
            sheet_info = []
            for sheet in sheet_names:
                temp_df = pd.read_excel(uploaded_file, sheet_name=sheet)
                sheet_info.append({
                    "Sheet Name": sheet,
                    "Number of Rows": len(temp_df),
                    "Number of Columns": len(temp_df.columns)
                })
            st.dataframe(
                pd.DataFrame(sheet_info),
                use_container_width=True,
                hide_index=True
            )
            
            # Add sheet selector
            selected_sheet = st.selectbox("Select Sheet for Detailed Analysis", sheet_names)
            
            # Read the selected sheet without dtype_backend parameter
            df = pd.read_excel(
                uploaded_file, 
                sheet_name=selected_sheet
            )
        else:
            # Read CSV without dtype_backend parameter
            df = pd.read_csv(uploaded_file)
        
        # Convert object columns to string type for better Arrow compatibility
        for col in df.select_dtypes(include=['object']):
            df[col] = df[col].astype(str)
        
        # Display basic info
        st.subheader("Data Overview")
        st.write(f"Total Records: {len(df)}")
        st.dataframe(df.head())
        
        # Basic analysis
        st.subheader("Data Analysis")
        
        # Select columns for analysis
        numeric_cols = df.select_dtypes(include=['float64', 'int64', 'Float64', 'Int64']).columns.tolist()
        
        if numeric_cols:  # Check if there are any numeric columns
            selected_col = st.selectbox("Select column for analysis", numeric_cols)
            
            # Handle null values for statistics
            valid_data = df[selected_col].dropna()
            
            # Basic statistics
            col1, col2, col3 = st.columns(3)
            col1.metric("Mean", round(valid_data.mean(), 2))
            col2.metric("Median", round(valid_data.median(), 2))
            col3.metric("Std Dev", round(valid_data.std(), 2))
            
            # Visualizations
            st.subheader("Visualizations")
            
            # Histogram with better handling of null values
            fig_hist = px.histogram(
                valid_data, 
                title=f"Distribution of {selected_col}",
                labels={selected_col: selected_col}
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
            # Time series if date column exists
            date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            if date_cols:
                date_col = st.selectbox("Select date column", date_cols)
                fig_time = px.line(
                    df.dropna(subset=[date_col, selected_col]), 
                    x=date_col, 
                    y=selected_col,
                    title=f"{selected_col} over time"
                )
                st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.warning("No numeric columns found in the dataset. Please upload a file with numeric data.")
        
        # Display column information
        st.subheader("Column Information")
        col_info = pd.DataFrame({
            'Type': df.dtypes.astype(str),  # Convert dtype objects to strings
            'Non-Null Count': df.count().astype(int),  # Ensure counts are integers
            'Null Count': df.isna().sum().astype(int),  # Ensure counts are integers
            'Sample Values': [df[col].head(1).iloc[0] if len(df[col]) > 0 else None for col in df.columns]
        })
        
        # Convert the entire dataframe to strings for better Arrow compatibility
        col_info = col_info.astype(str)
        
        # Display with better formatting
        st.dataframe(
            col_info,
            use_container_width=True,
            hide_index=False,
            column_config={
                "Type": st.column_config.TextColumn("Data Type"),
                "Non-Null Count": st.column_config.TextColumn("Non-Null Count"),
                "Null Count": st.column_config.TextColumn("Null Count"),
                "Sample Values": st.column_config.TextColumn("Sample Value")
            }
        )
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.write("Please make sure your file is properly formatted and try again.")

# Add installation instructions for better performance
if st.sidebar.checkbox("Show Installation Instructions"):
    st.sidebar.markdown("""
    ### For better performance:
    
    Install Watchdog:
    ```bash
    xcode-select --install
    pip install watchdog
    ```
    """)