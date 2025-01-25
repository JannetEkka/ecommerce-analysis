import pandas as pd
from pathlib import Path
import glob
import sys
from datetime import datetime

def combine_checkpoint_files():
    print("\n=== Laptop Data Checkpoint Combiner ===\n")
    
    # Get project root directory (3 levels up from this script in data_utils)
    current_dir = Path(__file__).resolve()
    project_root = current_dir.parent.parent.parent
    data_dir = project_root / 'data' / 'raw'
    
    # Create output directory if it doesn't exist
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all checkpoint CSV files
    checkpoint_files = glob.glob(str(data_dir / 'laptop_data_checkpoint_*.csv'))
    
    if not checkpoint_files:
        print("No checkpoint files found in data/raw directory!")
        print(f"Looking in: {data_dir}")
        return
        
    print(f"Found {len(checkpoint_files)} checkpoint files:")
    for file in checkpoint_files:
        print(f"- {Path(file).name}")
        
    # Read and combine all files
    print("\nReading and combining files...")
    dataframes = []
    total_rows = 0
    
    for file in checkpoint_files:
        try:
            df = pd.read_csv(file)
            total_rows += len(df)
            # Add source file information
            df['source_file'] = Path(file).name
            dataframes.append(df)
            print(f"Read {len(df)} rows from {Path(file).name}")
        except Exception as e:
            print(f"Error reading {Path(file).name}: {str(e)}")
            continue
    
    if not dataframes:
        print("No data could be read from checkpoint files!")
        return
        
    # Combine all dataframes
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # Remove duplicates based on URL
    print("\nRemoving duplicates...")
    before_dedup = len(combined_df)
    combined_df.drop_duplicates(subset=['url'], keep='first', inplace=True)
    duplicates_removed = before_dedup - len(combined_df)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = data_dir / f'raw_combined_data_{timestamp}.csv'
    
    # Save combined data
    combined_df.to_csv(output_file, index=False)
    
    # Print statistics
    print("\nCombination Complete!")
    print("-" * 40)
    print(f"Total input rows: {total_rows}")
    print(f"Duplicates removed: {duplicates_removed}")
    print(f"Final rows after deduplication: {len(combined_df)}")
    print(f"Total columns: {len(combined_df.columns)}")
    print(f"Data from {len(checkpoint_files)} checkpoint files")
    print("-" * 40)
    print(f"\nSaved combined data to: {output_file}")

if __name__ == "__main__":
    try:
        combine_checkpoint_files()
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)