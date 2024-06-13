# E-commerce Data Scraper and Analysis

This project is a web scraper for collecting e-commerce data from Amazon using Selenium and Python. It includes the following steps:

1. **Web Scraping**: Using Selenium to scrape product data from multiple pages.
2. **Data Storage**: Storing the scraped data in an SQL database (SQLite).
3. **Data Analysis and Visualization**: Retrieving data from the SQL database and performing EDA using pandas, matplotlib, and seaborn.

## Project Structure
ecommerce-analysis/
│
├── data/ # Directory for data storage
│ ├── chromedriver-win64/ # Directory for the downloaded ChromeDriver
│ ├── chromedriver.exe # ChromeDriver executable
│ ├── LICENSE.chromedriver # License for ChromeDriver
├── ecommerce-analysis-venv/ # Virtual environment (not included in the repo)
├── .gitignore # Git ignore file
├── README.md # Project documentation
├── requirements.txt # Python dependencies
└── web_scraper.py # Main web scraping script

## License
[MIT License](LICENSE)
