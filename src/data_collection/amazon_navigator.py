from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from typing import List, Dict
import pandas as pd
from datetime import datetime
from pathlib import Path
from .rate_limiter import RateLimiter

class AmazonNavigator:
    def __init__(self):
        self.driver = None
        self.rate_limiter = RateLimiter(
            base_delay=2.0,
            max_delay=5.0,
            jitter_factor=0.3,
            backoff_factor=2,
            max_retries=3,
            min_request_interval=1.0
        )
        self.setup_driver()

    def setup_driver(self):
        """Initialize the webdriver with memory optimization"""
        chrome_options = webdriver.ChromeOptions()

        # Memory optimization options
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-browser-side-navigation')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')

        # Set process memory limits
        chrome_options.add_argument('--js-flags="--max-old-space-size=4096"')  

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)

    def start_navigation(self):
        """Start the navigation process"""
        try:
            # Go to Amazon homepage
            self.driver.get("https://www.amazon.in/")
            self.rate_limiter.wait("homepage_load")
        
            # Click on the hamburger menu (All)        
            menu_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "nav-hamburger-menu"))
            )
            menu_button.click()
            
            # Wait for the category menu to load
            self.rate_limiter.wait("menu_load")
            self.wait.until(
                EC.presence_of_element_located((By.ID, "hmenu-content"))
            )
            self.rate_limiter.record_success("start_navigation")

        except TimeoutException:
            self.rate_limiter.record_failure("start_navigation")
            print("Error: Couldn't load the main menu")
            return None

    def get_main_categories(self) -> List[str]:
        """Get list of main categories"""
        categories = []
        try:
            self.rate_limiter.wait("category_load")

            # Wait for and scroll to "Shop by Category" section
            shop_by_category = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(text(), 'Shop by Category')]")
                )
            )
            
            # Scroll to element using JavaScript
            self.driver.execute_script("arguments[0].scrollIntoView(true);", shop_by_category)
            self.rate_limiter.wait("scroll")
            
            # Find and click "See All"
            see_all = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[@class='hmenu-item hmenu-compressed-btn']")
                )
            )
            see_all.click()
            self.rate_limiter.wait("menu_expand")
            
            # Get all categories from the expanded menu
            category_elements = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//ul[contains(@class, 'hmenu-visible')]//a[@class='hmenu-item' and not(contains(@class, 'hmenu-back-button'))]")
                )
            )
            
            # Filter out empty text and special menu items
            categories = [
                elem.text for elem in category_elements 
                if elem.text and 
                not elem.text.startswith('Main') and
                not elem.text == 'See All'
            ]

            self.rate_limiter.record_success("get_categories")
                
        except Exception as e:
            self.rate_limiter.record_failure("get_categories")
            print(f"Error getting categories: {str(e)}")
                
        return categories

    def select_category(self, category_name: str) -> List[str]:
        """Select a category and get its subcategories"""
        subcategories = []
        try:
            self.rate_limiter.wait("category_selection")

            # Find and click the category
            category_link = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//ul[contains(@class, 'hmenu-visible')]//a[@class='hmenu-item'][.//div[contains(text(), '{category_name}')] or contains(text(), '{category_name}')]")
                )
            )
            category_link.click()
            self.rate_limiter.wait("submenu_load")
            
            # Wait for submenu to be visible
            self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//ul[contains(@class, 'hmenu-visible')]//div[@role='heading']")
                )
            )
            
            # Get all elements in order (headings and items)
            menu_elements = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, """//ul[contains(@class, 'hmenu-visible')]/li[
                        .//div[@role='heading'] or 
                        .//a[@class='hmenu-item' and not(contains(@class, 'hmenu-back-button'))] or
                        @class='hmenu-separator'
                    ]""")
                )
            )
            
            current_section = None
            for element in menu_elements:
                try:
                    # Check if it's a heading
                    heading = element.find_elements(By.XPATH, ".//div[@role='heading']")
                    if heading and heading[0].text:
                        current_section = f"=== {heading[0].text} ==="
                        subcategories.append(current_section)
                        continue
                    
                    # Check if it's a separator
                    if element.get_attribute("class") == "hmenu-separator":
                        continue
                    
                    # Must be a regular item
                    item = element.find_elements(By.XPATH, ".//a[@class='hmenu-item']")
                    if item and item[0].text and not item[0].text.startswith('Main'):
                        subcategories.append(item[0].text)
                        
                except Exception as e:
                    print(f"Error processing menu element: {str(e)}")
                    continue

            self.rate_limiter.record_success("select_category")
                        
        except Exception as e:
            self.rate_limiter.record_failure("select_category")
            print(f"Error selecting category: {str(e)}")
            
        return subcategories
    
    def select_subcategory(self, subcategory_name: str):
        """
        Select a specific subcategory after a main category has been selected.
        Should be called after select_category().
        """
        try:
            self.rate_limiter.wait("subcategory_selection")
            
            # Use JavaScript to find and click the laptops link using specific selector
            js_click_cmd = '''
                const element = document.querySelector("#hmenu-content > ul.hmenu.hmenu-visible.hmenu-translateX > li:nth-child(17) > a");
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    setTimeout(() => {
                        element.click();
                    }, 1000);
                }
                return !!element;
            '''
            success = self.driver.execute_script(js_click_cmd)
            
            if not success:
                self.rate_limiter.record_failure("subcategory_selection")
                raise Exception(f"Could not find subcategory element {subcategory_name}")
                
            self.rate_limiter.wait("subcategory_load")
            self.rate_limiter.record_success("subcategory_selection")
            
        except Exception as e:
            print(f"Error selecting subcategory {subcategory_name}: {str(e)}")

    @staticmethod
    def save_refinements_to_csv(refinements_data: Dict[str, List[str]], category: str, filename: str = None):
        """
        Save refinements data to CSV file
        Args:
            refinements_data (Dict[str, List[str]]): Dictionary of refinement categories and their options
            category (str): The main category being scraped
            filename (str, optional): Name of output CSV file. Defaults to None.
        Returns:
            Path: Path to the saved CSV file
        """
        # Create timestamp for filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate filename if not provided
        if not filename:
            filename = f"refinements_{category.lower().replace(' ', '_')}_{timestamp}.csv"
        
        # Ensure the data/raw directory exists
        raw_dir = Path(__file__).parent.parent.parent / 'data' / 'raw'
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        # Create full file path
        file_path = raw_dir / filename
        
        # Create a list to store flattened refinement data
        flattened_data = []
        
        # Flatten the refinements dictionary for CSV format
        for category_name, options in refinements_data.items():
            for option in options:
                flattened_data.append({
                    'category': category_name,
                    'option': option,
                    'scrape_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # Convert to DataFrame
        df = pd.DataFrame(flattened_data)
        
        # Save to CSV
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"\nRefinements data saved to {file_path}")
        print(f"Total refinement categories: {len(refinements_data)}")
        print(f"Total refinement options: {len(flattened_data)}")
        return file_path

    def get_refinements(self) -> Dict[str, List[str]]:
        """Get all refinement options from left panel"""
        refinements = {}
        try:
            self.rate_limiter.wait("refinements_load")

            # Wait for refinements panel
            self.wait.until(
                EC.presence_of_element_located((By.ID, "s-refinements"))
            )
            
            self.rate_limiter.wait("refinements_process")
            
            # Get all refinement groups using role="group"
            groups = self.driver.find_elements(By.XPATH, "//div[@role='group']")
            
            for group in groups:
                try:
                    # Get group title (first div contains the title)
                    title_elem = group.find_element(By.XPATH, "./div")
                    title = title_elem.text.strip()
                    
                    # Get all options from the ul list
                    options = group.find_elements(
                        By.XPATH,
                        ".//ul//span[@class='a-size-base a-color-base']"
                    )
                    
                    # Only add groups that have both title and options
                    if title and options:
                        refinements[title] = [opt.text.strip() for opt in options if opt.text.strip()]
                        
                except NoSuchElementException:
                    continue
                    
            self.rate_limiter.record_success("get_refinements")
            return refinements
            
        except Exception as e:
            self.rate_limiter.record_failure("get_refinements")
            print(f"Error getting refinements: {str(e)}")
            return {}
        
    def get_results(self):
        """Navigate to full results page after selecting subcategory"""
        try:
            self.rate_limiter.wait("results_load")
            
            # Find and scroll to "See all results" link
            see_all_results = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//span[contains(text(), 'See all results')]")
                )
            )
            
            # Scroll the element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", see_all_results)
            self.rate_limiter.wait("scroll")
            
            # Click the element
            self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(), 'See all results')]")
            )).click()

            self.rate_limiter.wait("results_page_load")
            
            # Wait for results page to load by checking for Results heading
            self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@class='sg-col-inner']//h2[contains(text(), 'Results')]")
                )
            )
            
            self.rate_limiter.record_success("get_results")
            return True
                
        except TimeoutException as e:
            self.rate_limiter.record_failure("get_results")
            print(f"Timeout while getting results: {str(e)}")
            return False
        except Exception as e:
            self.rate_limiter.record_failure("get_results")
            print(f"Error getting results: {str(e)}")
            return False
        
    def collect_product_data(self, max_products=None, start_page=1):
        """
        Collect both basic and detailed product data in a single pass
        Args:
            max_products (int): Maximum number of products to process
        Returns:
            list: List of dictionaries containing complete product data
        """
        products_data = []
        current_page = 1
        main_window = None
        checkpoint_size = 20
        products_count = 0  # Debug counter

        print("\nDEBUG: Starting data collection")
        print(f"DEBUG: Checkpoint size set to: {checkpoint_size}")
        
        try:
            # If starting from a specific page, navigate there first
            if start_page > 1:
                # Navigate to the specific page (we'll implement this)
                self._navigate_to_page(start_page)
            while True:
                self.rate_limiter.wait(f"page_load_{current_page}")

                # Wait for results to load
                self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='listitem']")))
                main_window = self.driver.current_window_handle
                
                print(f"\nDEBUG: Processing page {current_page}")
                print(f"DEBUG: Current total products: {products_count}")
                
                # Get all products on current page
                product_items = self.driver.find_elements(By.XPATH, "//div[@role='listitem']")
                print(f"DEBUG: Found {len(product_items)} items on current page")
                
                # Process each product on the page
                for i, item in enumerate(product_items, 1):
                    if max_products and len(products_data) >= max_products:
                        print(f"\nReached maximum products limit ({max_products})")
                        return products_data
                        
                    try:
                        # Add rate limiting delay between products
                        self.rate_limiter.wait(f"product_process_{current_page}_{i}")
                        
                        product_data = {}

                        # Check if item is sponsored
                        try:
                            sponsored_check = item.find_element(By.XPATH, ".//span[@class='a-color-secondary' and contains(@aria-label, 'Sponsored')]")
                            print(f"DEBUG: Skipping sponsored product at position {i}")
                            continue
                        except NoSuchElementException:
                            print(f"DEBUG: Product {i} is not sponsored")
                        
                        # Extract basic data
                        try:
                            product_data['title'] = item.find_element(By.CSS_SELECTOR, 'div[data-cy="title-recipe"]').text
                            product_data['url'] = item.find_element(By.CSS_SELECTOR, 'div[data-cy="title-recipe"] a').get_attribute('href')
                            product_data['price'] = item.find_element(By.XPATH, './/div[@data-cy="price-recipe"]//span[contains(@class, "a-price-whole")]').text
                        except Exception as e:
                            print(f"Error extracting basic data for product {i}: {str(e)}")
                            continue
                        
                        print(f"\nProcessing product {len(products_data) + 1}: {product_data['title'][:50]}...")
                        
                        # Add delay before opening new tab
                        self.rate_limiter.wait("new_tab")

                        # Open product page in new tab
                        self.driver.execute_script(f"window.open('{product_data['url']}', '_blank');")
                        time.sleep(2)
                        
                        # Switch to new tab
                        self.rate_limiter.wait("tab_switch")
                        new_tab = [handle for handle in self.driver.window_handles if handle != main_window][-1]
                        self.driver.switch_to.window(new_tab)
                        
                        # Extract detailed data
                        try:
                            product_data['technical_details'] = {}
                            product_data['additional_info'] = {}
                            
                            # Get Technical Details
                            try:
                                self.rate_limiter.wait("tech_details")
                                tech_table = self.driver.find_element(By.ID, 'productDetails_techSpec_section_1')
                                rows = tech_table.find_elements(By.TAG_NAME, 'tr')
                                for row in rows:
                                    label = row.find_element(By.TAG_NAME, 'th').text.strip()
                                    value = row.find_element(By.TAG_NAME, 'td').text.strip()
                                    product_data['technical_details'][label] = value
                            except Exception as e:
                                print(f"No technical details found: {str(e)}")
                                
                            # Get Additional Information
                            try:
                                self.rate_limiter.wait("additional_info")
                                info_table = self.driver.find_element(By.ID, 'productDetails_detailBullets_sections1')
                                rows = info_table.find_elements(By.TAG_NAME, 'tr')
                                for row in rows:
                                    label = row.find_element(By.TAG_NAME, 'th').text.strip()
                                    value = row.find_element(By.TAG_NAME, 'td').text.strip()
                                    product_data['additional_info'][label] = value
                            except Exception as e:
                                print(f"No additional info found: {str(e)}")
                                
                        except Exception as e:
                            print(f"Error extracting detailed data: {str(e)}")
                        
                        # Close product tab and switch back
                        self.driver.close()
                        self.rate_limiter.wait("tab_switch_back")
                        self.driver.switch_to.window(main_window)
                        
                        # Add product data to list
                        products_data.append(product_data)
                        self.rate_limiter.record_success(f"product_{current_page}_{i}")
                        print(f"Successfully collected all data for product {len(products_data)}")

                        # After successful product processing
                        products_count += 1
                        print(f"\nDEBUG: Successfully processed product {products_count}")
                        print(f"DEBUG: Length of products_data: {len(products_data)}")
                        print(f"DEBUG: Modulo calculation: {len(products_data)} % {checkpoint_size} = {len(products_data) % checkpoint_size}")
                        
                        # Checkpoint logic with debug
                        if len(products_data) % checkpoint_size == 0:
                            print(f"\nDEBUG: Checkpoint condition met!")
                            print(f"DEBUG: About to save checkpoint at {products_count} products")
                            try:
                                checkpoint_file = self.save_to_csv(
                                    products_data,
                                    f"laptop_data_checkpoint_p{current_page}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                                )
                                print(f"DEBUG: Checkpoint successfully saved to: {checkpoint_file}")
                            except Exception as e:
                                print(f"DEBUG: Error saving checkpoint: {str(e)}")

                    except Exception as e:
                        print(f"DEBUG: Error processing product {i} on page {current_page}: {str(e)}")
                        self.rate_limiter.record_failure(f"product_{current_page}_{i}")
                        # Ensure we're back on main window
                        if self.driver.current_window_handle != main_window:
                            self.driver.close()
                            self.driver.switch_to.window(main_window)
                        continue
                
                # Check for next page
                try:
                    self.rate_limiter.wait("pagination")
                    
                    # Try multiple selectors for the next button
                    next_button = None
                    selectors = [
                        # By role and aria-label (most reliable)
                        "//a[@role='button' and contains(@aria-label, 'Go to next page')]",
                        # By class and text
                        "//a[contains(@class, 's-pagination-next') and contains(text(), 'Next')]",
                        # By the specific class combination
                        "//a[@class='s-pagination-item s-pagination-next s-pagination-button s-pagination-button-accessibility s-pagination-separator']"
                    ]
                    
                    for selector in selectors:
                        try:
                            next_button = self.wait.until(
                                EC.presence_of_element_located((By.XPATH, selector))
                            )
                            if next_button:
                                break
                        except:
                            continue
                            
                    if not next_button:
                        print("\nNo next button found - reached last page")
                        break
                        
                    # Scroll the button into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    self.rate_limiter.wait("scroll_to_next")
                    
                    # Click using JavaScript for better reliability
                    self.driver.execute_script("arguments[0].click();", next_button)
                    
                    self.rate_limiter.wait("page_transition")
                    current_page += 1
                    print(f"\nMoving to page {current_page}...")
                    
                    # Wait for the new page to load by checking URL change or new results
                    self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//div[@data-cy='title-recipe']"))
                    )
                    
                except Exception as e:
                    print(f"Error during pagination: {str(e)}")
                    break
            
            return products_data
            
        except Exception as e:
            print(f"DEBUG: Major error in collection: {str(e)}")
            print(f"DEBUG: Final products count: {products_count}")
            print(f"DEBUG: Final products_data length: {len(products_data)}")
            # Handle window switching
            if main_window in self.driver.window_handles:
                self.driver.switch_to.window(main_window)
            return products_data
        finally:
            print("\nDEBUG: Collection ended")
            print(f"DEBUG: Final totals - Counter: {products_count}, Data Length: {len(products_data)}")

    def _navigate_to_page(self, target_page):
        """Navigate to a specific page number using sequential navigation"""
        try:
            # First ensure we're on the search results page
            if not self.driver.current_url.startswith("https://www.amazon.in/s?"):
                self.get_results()
                
            # Get current page
            try:
                current_page_element = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//span[@class='s-pagination-item s-pagination-selected']"))
                )
                current_page = int(current_page_element.text)
                print(f"\nCurrently on page {current_page}, navigating to page {target_page}")
            except Exception as e:
                print(f"Could not determine current page: {str(e)}")
                current_page = 1

            # Navigate page by page until we reach target
            while current_page < target_page:
                try:
                    # Find and click the next page button
                    next_button = self.wait.until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//a[contains(@class, 's-pagination-next')]")
                        )
                    )
                    
                    # Scroll the button into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    self.rate_limiter.wait("scroll_to_next")
                    
                    # Click the next button
                    next_button.click()
                    
                    # Wait for page to load and update current page
                    self.rate_limiter.wait("page_load")
                    current_page += 1
                    print(f"Successfully navigated to page {current_page}")
                    
                    # Verify current page
                    self.wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, f"//span[@class='s-pagination-item s-pagination-selected' and text()='{current_page}']")
                        )
                    )
                    
                except Exception as e:
                    print(f"Error during navigation at page {current_page}: {str(e)}")
                    raise

            return True

        except Exception as e:
            print(f"Error in page navigation: {str(e)}")
            raise

    @staticmethod
    def save_to_csv(products_data, filename="laptop_data.csv"):
        """
        Save product data to CSV file
        Args:
            products_data (list): List of product dictionaries
            filename (str): Name of output CSV file
        """
        
        # Ensure the data/raw directory exists
        raw_dir = Path(__file__).parent.parent.parent / 'data' / 'raw'
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        # Create full file path
        file_path = raw_dir / filename

        # Create a list to store flattened data
        flattened_data = []
        
        for product in products_data:
            # Start with basic fields
            product_dict = {
                'title': product.get('title', ''),
                'price': product.get('price', ''),
                'url': product.get('url', ''),
                'scrape_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Add technical details with 'tech_' prefix
            for key, value in product.get('technical_details', {}).items():
                product_dict[f'tech_{key}'] = value
                
            # Add additional info with 'info_' prefix
            for key, value in product.get('additional_info', {}).items():
                product_dict[f'info_{key}'] = value
                
            flattened_data.append(product_dict)
        
        # Convert to DataFrame
        df = pd.DataFrame(flattened_data)
        
        # Save to CSV
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"\nData saved to {file_path}")
        print(f"Total products saved: {len(flattened_data)}")
        print(f"Total columns: {len(df.columns)}")
        return file_path

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()