import logging
import sys
import re
import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv



# ---------------------------
# Setup Logging Configuration
# ---------------------------
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# ---------------------------
# Utility Functions
# ---------------------------
def clean_text(text):
    """
    Cleans text by stripping extra whitespace, removing special characters,
    and replacing multiple spaces with a single space.
    """
    if isinstance(text, str):
        text = text.strip()
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text
    return text

# ---------------------------
# ETL Functions
# ---------------------------
def load_data(csv_path):
    """
    Loads CSV data into a DataFrame.
    """
    try:
        df = pd.read_csv(csv_path)
        logging.info("CSV loaded successfully from %s", csv_path)
        return df
    except Exception as e:
        logging.error("Error reading CSV file: %s", e)
        sys.exit(1)

def remove_duplicates(df):
    """
    Removes duplicate rows from the DataFrame.
    """
    before = df.shape[0]
    df = df.drop_duplicates()
    after = df.shape[0]
    logging.info("Removed %d duplicate rows", before - after)
    return df

def handle_missing_values(df):
    """
    Handles missing values by filling missing PrimaryColor with 'Unknown'.
    """
    df['PrimaryColor'] = df['PrimaryColor'].fillna('Unknown')
    return df

def correct_data_types(df):
    """
    Corrects data types for specified columns.
    """
    try:
        df['ProductID'] = df['ProductID'].astype(str)
        df['Price (INR)'] = pd.to_numeric(df['Price (INR)'], errors='coerce')
    except Exception as e:
        logging.error("Error converting data types: %s", e)
        sys.exit(1)
    return df

def remove_brand_prefix(df):
    """
    Removes the brand name from the start of the product name if present.
    """
    def remove_prefix(row):
        brand = row['ProductBrand'].strip()
        product_name = row['ProductName'].strip()
        if product_name.lower().startswith(brand.lower()):
            return product_name[len(brand):].strip()
        return product_name

    df['ProductName'] = df.apply(remove_prefix, axis=1)
    return df

def standardize_text_fields(df):
    """
    Standardizes text fields by cleaning and applying case conventions.
    """
    # For ProductBrand: strip, title-case, then clean
    df['ProductBrand'] = df['ProductBrand'].str.strip().str.title().apply(clean_text)
    # For ProductName: strip, lowercase, then clean
    df['ProductName'] = df['ProductName'].str.strip().str.lower().apply(clean_text)
    # For Gender and PrimaryColor: strip and convert to lowercase
    df['Gender'] = df['Gender'].str.strip().str.lower()
    df['PrimaryColor'] = df['PrimaryColor'].str.strip().str.lower()
    # Clean the Description field
    df['Description'] = df['Description'].apply(clean_text)
    return df

def categorize_price(df):
    """
    Categorizes the Price (INR) into Low, Medium, and High based on quantiles.
    """
    low_threshold = df['Price (INR)'].quantile(0.33)
    high_threshold = df['Price (INR)'].quantile(0.66)
    bins = [df['Price (INR)'].min() - 1, low_threshold, high_threshold, df['Price (INR)'].max() + 1]
    labels = ['Low', 'Medium', 'High']
    df['PriceCategory'] = pd.cut(df['Price (INR)'], bins=bins, labels=labels)
    return df

def filter_invalid_primary_color(df):
    """
    Filters out rows with missing or invalid PrimaryColor values.
    """
    before = df.shape[0]
    df_filtered = df[
        df['PrimaryColor'].notna() &
        (df['PrimaryColor'].str.strip() != '') &
        (df['PrimaryColor'].str.lower() != 'unknown')
    ]
    logging.info("Filtered out %d rows with invalid PrimaryColor", before - df_filtered.shape[0])
    return df_filtered

def load_to_mysql(df, engine, table_name='products'):
    """
    Loads the DataFrame into a MySQL table using SQLAlchemy.
    """
    try:
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
        logging.info("Data loaded successfully into MySQL table '%s'", table_name)
    except SQLAlchemyError as e:
        logging.error("Error loading data to MySQL: %s", e)
        sys.exit(1)

# ---------------------------
# Main ETL Process
# ---------------------------
def main():

    # load_dotenv(override=True)

    # Database connection parameters
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    host = os.getenv("HOST")
    port = os.getenv("PORT")
    database = os.getenv("DATABASE")
    connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    print("Connection string:", connection_string)
    
    # Create SQLAlchemy engine
    engine = create_engine(connection_string)
    
    # CSV file path
    csv_path = os.getenv("CSV_PATH")
    
    # ETL Process
    df = load_data(csv_path)
    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = correct_data_types(df)
    df = remove_brand_prefix(df)
    df = standardize_text_fields(df)
    
    # NOTE: Task 5 (outlier handling) was not implemented in your code.
    # If needed, add outlier handling here.
    
    df = categorize_price(df)
    df = filter_invalid_primary_color(df)
    
    # Load the cleaned data into MySQL
    load_to_mysql(df, engine)
    
    logging.info("ETL pipeline completed successfully.")

if __name__ == "__main__":
    main()
