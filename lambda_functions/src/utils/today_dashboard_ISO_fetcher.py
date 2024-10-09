from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from tempfile import mkdtemp
import pandas as pd
from datetime import datetime, timedelta
import os


class FangraphsDashboardScraper:

    @staticmethod
    def fetch_data(url):
        chrome_options = ChromeOptions()

        chrome_options.add_argument("--headless=new")  # Use new headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--no-zygote")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument(f"--user-data-dir={mkdtemp()}")
        chrome_options.add_argument(f"--data-path={mkdtemp()}")
        chrome_options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        chrome_options.add_argument("--remote-debugging-pipe")
        chrome_options.add_argument("--window-size=1920,1080")  # Set proper window size
        chrome_options.add_argument("--verbose")
        chrome_options.add_argument("--log-path=/tmp/chrome.log")
        chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"

        service = ChromeService(
            executable_path="/opt/chrome-driver/chromedriver-linux64/chromedriver",
        )

        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )

        try:
            # Fetch the webpage
            driver.get(url)

            # Wait for the table to load on the page
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".fg-data-grid.table-type tbody tr"))
            )

            # Extract the HTML content of the page
            html_content = driver.page_source
        finally:
            # Ensure the driver quits to release resources
            driver.quit()

        return html_content

    @staticmethod
    def parse_data(html_content, data_type, date):
        """
        Parses the data from the Fangraphs website and adds the date.
        Args:
            html_content (str): The HTML content to parse.
            data_type (str): Type of data to extract (e.g., 'iso' for Fly Ball%).
            date (str): The date to add to the data (formatted as YYYY-MM-DD).
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        table_div = soup.find('div', {'class': 'fg-data-grid table-type'})
        rows = table_div.find('table').find_all('tr', class_=True)
        data = []
        batter_id = 1  # Start with batter_id 1, increment for each batter
        for row in rows:
            columns = row.find_all('td')
            batter_name = columns[1].text.strip()  # Get batter name
            team = columns[2].text.strip()  # Get team name
            iso = columns[12].text.strip()  # Get Fly Ball percentage (iso%)
            # remove . from iso
            iso = iso.replace(".", "")
            # Append the parsed data
            data.append({
                'batter': batter_name,
                'iso': iso,
                'team': team,
                'batter_id': batter_id,
                'date': date  # Add the date
            })
            batter_id += 1  # Increment batter_id for the next batter
        return data

    @staticmethod
    def save_data(data, file_path="iso_data.csv"):
        """
        Save the data to a CSV file.
        Args:
            data (list): The data to save.
            file_path (str): The file path to save the data.
        """
        df = pd.DataFrame(data)  # Convert list of dictionaries to DataFrame
        # Check if file exists. If it does, don't write the header again.
        if os.path.exists(file_path):
            df.to_csv(file_path, mode='a', index=False, header=False)
        else:
            df.to_csv(file_path, mode='a', index=False, header=True)

    @staticmethod
    def generate_url(base_url, start_date):
        """
        Generate the URL with the specific date range for the 3/28 batter FB%.
        Args:
            base_url (str): The base URL to append the date range to.
            start_date (str): The specific date for the data.
        Returns:
            str: The generated URL.
        """
        # Set the start and end date as 3/28
        # Parse the start date string to a datetime object
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')

        # Set end date to 15 days after the start date
        end_date_obj = start_date_obj + timedelta(days=14)

        # Format the dates back to 'YYYY-MM-DD' for URL usage
        start_date_str = start_date_obj.strftime('%Y-%m-%d')
        end_date_str = end_date_obj.strftime('%Y-%m-%d')
        return f"{base_url}?pos=all&stats=bat&lg=all&season=2024&season1=2024&ind=0&team=0&pageitems=2000000000&qual=5&type=8&month=1000&startdate={start_date_str}&enddate={end_date_str}"

    @staticmethod
    def get_batter_iso_for_date(date, file_path="iso_data.csv"):
        """
        Fetch Fly Ball% for batters on a specific date and add the date to the data.
        Args:
            date (str): The date in the format 'YYYY-MM-DD'.
            file_path (str): The file path to save the data.
        """
        base_url = "https://www.fangraphs.com/leaders/major-league"
        url = FangraphsDashboardScraper.generate_url(base_url, date)
        print(url)

        # Calculate the date 16 days after the input date
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        final_date = (date_obj + timedelta(days=15)).strftime('%Y-%m-%d')

        # Fetch the data
        html_content = FangraphsDashboardScraper.fetch_data(url)
        if html_content:
            # Parse and process the Fly Ball% data
            parsed_data = FangraphsDashboardScraper.parse_data(
                html_content, data_type="iso", date=final_date)
            FangraphsDashboardScraper.save_data(parsed_data, file_path)
            return parsed_data

