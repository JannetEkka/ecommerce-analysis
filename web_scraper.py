import os
import shutil
import subprocess
import re
import requests
import zipfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
import time
from sqlalchemy import create_engine, Column, String, Float, Integer, MetaData, Table
from sqlalchemy.orm import sessionmaker

def get_chrome_version():
    try:
        output = subprocess.check_output(r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version', shell=True)
        version = re.search(r'version\s+REG_SZ\s+([^\s]+)', output.decode('utf-8')).group(1)
        return version
    except Exception as e:
        print(f"Error retrieving Chrome version: {e}")
        return None

def get_chrome_driver(chrome_version):
    try:
        # Extract the major version part
        major_version = '.'.join(chrome_version.split('.')[:-1])

        # Fetch the latest ChromeDriver version compatible with the major Chrome version
        response = requests.get(f'https://googlechromelabs.github.io/chrome-for-testing/latest-patch-versions-per-build-with-downloads.json')
        data = response.json()

        # Find the compatible ChromeDriver version
        if major_version in data['builds']:
            driver_version = data['builds'][major_version]['version']
            print(f"Found compatible ChromeDriver version: {driver_version}")
        else:
            print(f"No compatible ChromeDriver found for version {major_version}.")
            return False

        # Get the download URL for the win64 platform
        download_url = None
        for item in data['builds'][major_version]['downloads']['chromedriver']:
            if item['platform'] == 'win64':
                download_url = item['url']
                break

        if not download_url:
            print(f"Download URL for ChromeDriver on win64 not found.")
            return False

        # Download the ChromeDriver zip file
        driver_zip = 'chromedriver.zip'
        try:
            with requests.get(download_url, stream=True) as r:
                if r.status_code == 200:
                    with open(driver_zip, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
                else:
                    print(f"Failed to download ChromeDriver. Status code: {r.status_code}")
                    return False
        except Exception as e:
            print(f"Error downloading ChromeDriver: {e}")
            return False

        # Unzip the file and move the chromedriver to the data directory
        with zipfile.ZipFile(driver_zip, 'r') as zip_ref:
            zip_ref.extractall('data')

        os.remove(driver_zip)

        return True
    except Exception as e:
        print(f"Error retrieving ChromeDriver: {e}")
        return False

# Get the current Chrome version
chrome_version = get_chrome_version()
if chrome_version:
    print(f"Detected Chrome version: {chrome_version}")
    if get_chrome_driver(chrome_version):
        print(f"ChromeDriver for version {chrome_version} downloaded successfully.")
    else:
        print("Failed to download ChromeDriver.")
else:
    print("Failed to retrieve Chrome version.")

# Set up Selenium WebDriver
driver_path = './data/chromedriver-win64/chromedriver.exe'  # Path to ChromeDriver in the data folder
service = Service(driver_path)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode (optional)

try:
    driver = webdriver.Chrome(service=service, options=options)
except Exception as e:
    print(f"Error initializing WebDriver: {e}")
    exit(1)

# Function to scrape a page
def scrape_page(url):
    driver.get(url)
    time.sleep(5)  # Wait for the page to load

    products = driver.find_elements(By.XPATH, '//div[@data-component-type="s-search-result"]')
    data = []

    for product in products:
        try:
            name = product.find_element(By.XPATH, './/span[@class="a-size-medium a-color-base a-text-normal"]').text
        except:
            name = "N/A"
        try:
            price = product.find_element(By.XPATH, './/span[@class="a-price-whole"]').text
        except:
            price = "N/A"
        data.append({'name': name, 'price': price})

    return data

# Scrape data from the first page and subsequent 10 pages
base_url = 'https://www.amazon.in/s?k=laptops'
all_data = []
for page in range(1, 11):
    url = f"{base_url}&page={page}"
    print(f"Scraping page {page}")
    page_data = scrape_page(url)
    all_data.extend(page_data)

# Close the WebDriver
driver.quit()

# Store data in a pandas DataFrame
df = pd.DataFrame(all_data)
print(df)

# Save DataFrame to a CSV file
df.to_csv('data/products.csv', index=False)

# Set up SQLAlchemy connection to SQLite database
DATABASE_URL = "sqlite:///data/ecommerce_data.db"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define the table schema
product_data_table = Table(
    'product_data', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String, nullable=False),
    Column('price', String, nullable=False)
)

# Create the table in the database
metadata.create_all(engine)

# Insert data into the table
Session = sessionmaker(bind=engine)
session = Session()

# Insert data from the DataFrame to the SQL database
for index, row in df.iterrows():
    ins = product_data_table.insert().values(name=row['name'], price=row['price'])
    session.execute(ins)

session.commit()
session.close()

print("Data inserted into the database successfully.")
