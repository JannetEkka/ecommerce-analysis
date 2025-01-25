from datetime import datetime
from src.data_collection import AmazonNavigator
import pytest

def test_navigation():
    """Test the Amazon navigation functionality"""
    with AmazonNavigator() as navigator:
        print("\n=== Amazon Product Navigator ===\n")
        navigator.start_navigation()
        
        # Get and display main categories
        print("\nLoading categories...")
        categories = navigator.get_main_categories()
        
        print("\nAll Available Categories:")
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category}")
            
        # First, navigate to Mobiles, Computers
        target_category = "Mobiles, Computers"
        print(f"\nLoading subcategories for {target_category}...")
        subcategories = navigator.select_category(target_category)
        
        print("\nSubcategories:")
        for subcategory in subcategories:
            print(f"  {subcategory}")
            
        # Now click on Laptops
        print("\nNavigating to Laptops...")
        navigator.select_subcategory("Laptops")
        
        # Get full results first
        print("\nGetting full results...")
        success = navigator.get_results()
        assert success, "Failed to get full results page"
        
        # Get refinement options
        print("\nGetting refinement options...")
        refinements = navigator.get_refinements()

        # Display all refinements
        print("\nAvailable Refinement Options:")
        print("-" * 40)
        for category, options in refinements.items():
            print(f"\n{category}:")
            for option in options:
                print(f"  • {option}")
        print("-" * 40)

        # Collect product data (both basic and detailed)
        print("\nCollecting product data...")
        products = navigator.collect_product_data(start_page=155)
        
        # After collecting the data
        if products:
            # Save to CSV
            csv_file = AmazonNavigator.save_to_csv(products, f"laptop_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            print(f"\nData has been saved to: {csv_file}")

        # Display collected data
        print("\nCollected Product Data:")
        print("=" * 80)
        for i, product in enumerate(products, 1):
            print(f"\nProduct {i}:")
            print("-" * 40)
            print(f"Title: {product['title']}")
            print(f"Price: {product['price']}")
            print(f"URL: {product['url']}")
            
            if product.get('technical_details'):
                print("\nTechnical Details:")
                print("-" * 20)
                for key, value in product['technical_details'].items():
                    print(f"{key}: {value}")
            
            if product.get('additional_info'):
                print("\nAdditional Information:")
                print("-" * 20)
                for key, value in product['additional_info'].items():
                    print(f"{key}: {value}")
            print("=" * 80)

        # Print summary
        print(f"\nSuccessfully collected data for {len(products)} products")
            
if __name__ == "__main__":
    pytest.main([__file__, "-v"])