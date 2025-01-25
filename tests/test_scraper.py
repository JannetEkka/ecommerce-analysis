from data_collection.amazon_navigator import AmazonScraper
import pandas as pd

def run_scraper():
    print("\n=== Amazon Product Scraper ===\n")
    
    # Get user inputs
    search_query = input("Enter the product you want to search for: ")
    max_pages = int(input("How many pages to scrape (1-20)? "))
    min_price = input("Minimum price (press Enter to skip): ")
    max_price = input("Maximum price (press Enter to skip): ")
    
    # Convert price inputs to float if provided
    price_filters = {}
    if min_price:
        price_filters['min_price'] = float(min_price)
    if max_price:
        price_filters['max_price'] = float(max_price)
        
    print("\nStarting scraper...")
    scraper = AmazonScraper()
    
    try:
        # Construct search URL with user's query
        search_url = f"https://www.amazon.in/s?k={search_query.replace(' ', '+')}"
        
        # Scrape products
        products_df = scraper.scrape_category(search_url, max_pages=max_pages)
        
        # Apply price filters if any
        if price_filters:
            if 'min_price' in price_filters:
                products_df = products_df[products_df['price'] >= price_filters['min_price']]
            if 'max_price' in price_filters:
                products_df = products_df[products_df['price'] <= price_filters['max_price']]
        
        # Save results
        filename = f"data/raw/amazon_{search_query.replace(' ', '_')}.csv"
        products_df.to_csv(filename, index=False)
        
        # Display summary
        print(f"\nFound {len(products_df)} products")
        print(f"Results saved to: {filename}")
        
        # Display first few results
        print("\nFirst few products found:")
        print(products_df[['title', 'price', 'rating']].head())
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        scraper.close()

if __name__ == "__main__":
    run_scraper()