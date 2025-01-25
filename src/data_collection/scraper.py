from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import yaml
import logging
import time
from pathlib import Path
from typing import Dict, Optional, List
from ..data_utils.data_exporters import save_to_csv

class EcommerceScraper:
    def __init__(self, config_path: str = "config/scraping_config.yml"):
        self.config = self._load_config(config_path)
        self.driver = None
        self.setup_logging()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load scraping configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            raise Exception(f"Failed to load config: {str(e)}")
    
    def setup_logging(self):
        """Configure logging based on config settings"""
        logging.basicConfig(
            level=self.config['logging']['level'],
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=self.config['logging']['file']
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize_driver(self):
        """Initialize Selenium WebDriver with configured options"""
        chrome_options = Options()
        if self.config['scraping']['headless']:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(self.config['scraping']['timeout'])
        
    def scrape_product(self, url: str) -> Optional[Dict]:
        """Scrape a single product page"""
        if not self.driver:
            self.initialize_driver()
            
        try:
            self.driver.get(url)
            selectors = self.config['target_sites'][0]['selectors']
            
            product_data = {
                'url': url,
                'title': self._safe_extract(selectors['product_title']),
                'price': self._safe_extract(selectors['price']),
                'rating': self._safe_extract(selectors['rating']),
                'reviews': self._safe_extract(selectors['reviews'])
            }
            
            self.logger.info(f"Successfully scraped product: {product_data['title']}")
            return product_data
            
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {str(e)}")
            return None
            
    def _safe_extract(self, selector: str, wait_time: int = 5) -> Optional[str]:
        """Safely extract content using explicit wait"""
        try:
            element = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element.text.strip()
        except TimeoutException:
            self.logger.warning(f"Timeout waiting for selector: {selector}")
            return None
        except NoSuchElementException:
            self.logger.warning(f"Element not found: {selector}")
            return None
    
    def scrape_category(self, category_url: str, max_products: int = 100) -> List[Dict]:
        """Scrape products from a category page"""
        products_data = []
        # Implementation for category scraping
        # This would involve pagination handling and product list extraction
        # To be implemented based on specific website structure
        return products_data
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            
    def __enter__(self):
        """Context manager entry"""
        self.initialize_driver()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

if __name__ == '__main__':
    # Example usage
    with EcommerceScraper() as scraper:
        # Example product URL - replace with actual target
        product_data = scraper.scrape_product("https://example.com/product")
        if product_data:
            print("Scraped data:", product_data)