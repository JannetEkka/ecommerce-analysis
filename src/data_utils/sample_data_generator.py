import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path

def ensure_data_directories():
    """Create necessary data directories if they don't exist"""
    # Get the project root directory (2 levels up from this script)
    project_root = Path(__file__).parent.parent.parent
    
    # Create data/sample directory if it doesn't exist
    sample_dir = project_root / 'data' / 'sample'
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    return sample_dir

def generate_ecommerce_data():
    # Set random seed for reproducibility
    np.random.seed(42)  

    # Generate dates for the last 12 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # Sample product categories and price range
    categories = {
        'Electronics': (100, 2000),
        'Clothing': (20, 200),
        'Books': (10, 50),
        'Home & Kitchen': (30, 500),
        'Sports': (25, 300)
    }

    # Generate product data
    products = []
    for category, (min_price, max_price) in categories.items():
        for i in range(20):
            products.append({
                'product_id': f'{category[:3].upper()}_{i+1:03d}',
                'product_name': f'{category} Product {i+1}',
                'category': category,
                'base_price': round(np.random.uniform(min_price, max_price), 2)
            })

    # Convert to DataFrame
    products_df = pd.DataFrame(products)

    # Generate sales data
    sales_data = []
    for date in dates:
        # Generate more sales for weekends
        num_sales = np.random.randint(50, 100) if date.weekday() >= 5 else np.random.randint(30, 70)

        for _ in range(num_sales):
            product = products_df.iloc[np.random.randint(0, len(products_df))]
            
            # Add some price variation
            price_variation = np.random.uniform(0.9, 1.1)
            actual_price = round(product['base_price'] * price_variation, 2)

            # Generate customer satisfaction metrics
            rating = np.random.randint(1, 6)
            reviewed = np.random.random() < 0.3  # 30% chance of leaving a review

            sales_data.append({
                'date': date,
                'product_id': product['product_id'],
                'product_name': product['product_name'],
                'category': product['category'],
                'quantity': np.random.randint(1, 5),
                'unit_price': actual_price,
                'rating': rating if reviewed else None,
                'reviewed': reviewed,
                'customer_id': f'CUST_{np.random.randint(1, 1001):04d}',  # 1000 possible customers
                'region': np.random.choice(['North', 'South', 'East', 'West', 'Central']),
                'payment_method': np.random.choice(['Credit Card', 'Debit Card', 'PayPal', 'Cash on Delivery'])
            })

    # Convert to sales DataFrame
    sales_df = pd.DataFrame(sales_data)

    # Calculate total amount for each sale
    sales_df['total_amount'] = sales_df['quantity'] * sales_df['unit_price']

    # Get the data directory path
    data_dir = ensure_data_directories()

    # Save to CSV using the correct path
    products_df.to_csv(data_dir / 'products.csv', index=False)
    sales_df.to_csv(data_dir / 'sales.csv', index=False)

    print(f"Files saved to: {data_dir}")
    return products_df, sales_df

if __name__ == '__main__':
    products_df, sales_df = generate_ecommerce_data()
    print(f"Generated {len(products_df)} products and {len(sales_df)} sales records")