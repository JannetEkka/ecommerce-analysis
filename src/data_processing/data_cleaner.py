import pandas as pd
from pathlib import Path

def standardize_indian_price(price: str) -> float:
    """
    Convert Indian formatted price string to standard float number
    Example: "1,82,990" -> 182990.0
    
    Args:
        price (str): Price string in Indian format (e.g., "1,82,990")
        
    Returns:
        float: Standardized price value
    """
    return float(str(price).replace(",", ""))

def clean_prices(df: pd.DataFrame, price_column: str = 'price') -> pd.DataFrame:
    """
    Clean price data in a dataframe by standardizing Indian price format
    
    Args:
        df (pd.DataFrame): Input dataframe containing price data
        price_column (str): Name of the price column (default: 'price')
        
    Returns:
        pd.DataFrame: DataFrame with cleaned price column
    """
    df = df.copy()
    df[price_column] = df[price_column].apply(standardize_indian_price)
    return df

def save_processed_data(df: pd.DataFrame, filename: str = 'processed_data.csv') -> Path:
    """
    Save processed data to CSV in the processed data directory
    
    Args:
        df (pd.DataFrame): DataFrame to save
        filename (str): Name of the output file
        
    Returns:
        Path: Path to the saved file
    """
    # Get the path to processed data directory
    processed_dir = Path(__file__).parent.parent.parent / 'data' / 'processed'
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Create full file path
    file_path = processed_dir / filename
    
    # Save to CSV
    df.to_csv(file_path, index=False)
    return file_path

if __name__ == "__main__":
    # Get the project root directory (3 levels up from this script)
    project_root = Path(__file__).parent.parent.parent
    
    # Construct path to the raw data file
    raw_data_path = project_root / 'data' / 'raw' / 'raw_combined_data_20250125_141300.csv'
    
    # Read the CSV file
    print("\nReading raw data...")
    df = pd.read_csv(raw_data_path)
    
    # Show sample of original prices
    print("\nOriginal price samples:")
    print(df[['title', 'price']].head())
    
    # Clean the prices
    print("\nCleaning prices...")
    cleaned_df = clean_prices(df)
    
    # Select only title and cleaned price columns
    processed_df = cleaned_df[['title', 'price']]
    
    # Show sample of processed data
    print("\nProcessed data samples:")
    print(processed_df.head())
    
    # Save to processed directory
    output_path = save_processed_data(processed_df, 'laptops_processed_v1.csv')
    print(f"\nSaved processed data to: {output_path}")
    print(f"Shape of processed data: {processed_df.shape}")