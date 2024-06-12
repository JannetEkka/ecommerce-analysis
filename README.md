# Ecommerce Analysis

This project aims to create an analytics dashboard for an e-commerce website, including web scraping, data analysis, and visualization.

## Project Structure
- `data/`: Folder to store scraped data or database files.
- `notebooks/`: Jupyter notebooks for EDA and visualization.
- `scripts/`: Python scripts for scraping and analysis.
- `tests/`: Test scripts for pytest.

## Setup
1. Create a virtual environment:
    ```bash
    python -m venv ecommerce-analysis-venv
    source ecommerce-analysis-venv/bin/activate
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
- Run the scraping script:
    ```bash
    python scripts/scrape_data.py
    ```

- Run tests:
    ```bash
    pytest tests/
    ```

## License
[MIT License](LICENSE)
