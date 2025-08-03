import time
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
    StaleElementReferenceException,
)
from bs4 import BeautifulSoup

# Add agmarknet_API to path for imports
# This setup assumes the script is run from a location where this relative path is valid.
# For example, if script is in /my_project/scrapers/ and API is in /my_project/agmarknet_API/
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "agmarknet_API"))

try:
    from agmarknet_API.utils import (
        validate_input,
        sanitize_input,
        format_price,
        clean_text_data,
        log_request,
    )
    from agmarknet_API.config import Config
except ImportError:
    print("Warning: agmarknet_API not found. Using fallback mock functions.")

    def validate_input(commodity, state, market):
        return []

    def sanitize_input(text):
        return text.strip() if text else ""

    def format_price(price):
        return price

    def clean_text_data(data):
        return data

    def log_request(commodity, state, market, success, record_count=0):
        pass

    class Config:
        MAX_DAYS_BACK = 30
        MIN_DAYS_BACK = 1
        SCRAPER_HEADLESS = True
        SCRAPER_TIMEOUT = 30


# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MarketDataScraper:
    def __init__(
        self,
        base_url: str = "https://agmarknet.gov.in/SearchCmmMkt.aspx",
        headless: bool = None,
        timeout: int = None,
    ):
        """
        Initialize the market data scraper with Selenium WebDriver
        Args:
            base_url: Base URL for the agmarknet website
            headless: Run browser in headless mode (uses Config if None)
            timeout: Timeout for web operations (uses Config if None)
        """
        self.base_url = base_url
        self.headless = (
            headless
            if headless is not None
            else getattr(Config, "SCRAPER_HEADLESS", True)
        )
        self.timeout = (
            timeout if timeout is not None else getattr(Config, "SCRAPER_TIMEOUT", 30)
        )
        self.driver = None

    def _setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome driver with optimized options"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")

            # Performance optimizations
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            # Disabling images can speed up scraping but may break some sites.
            # Agmarknet works well even with images disabled for this specific task.
            chrome_options.add_argument("--blink-settings=imagesEnabled=false")
            # NOTE: Disabling JavaScript will break the site's postback mechanism for markets.

            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )

            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(self.timeout)
            driver.implicitly_wait(5)  # Set a smaller implicit wait

            logger.info("Chrome driver initialized successfully.")
            return driver
        except WebDriverException as e:
            logger.error(
                f"Failed to setup Chrome driver. Ensure chromedriver is in your PATH or installed. Error: {e}"
            )
            raise

    def _get_dropdown_options(
        self, element_id: str, default_option_text: str = "--Select--"
    ) -> List[str]:
        """
        A generic helper to scrape all options from a dropdown menu.
        """
        driver = self._setup_driver()
        options_list = []
        try:
            driver.get(self.base_url)
            dropdown_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, element_id))
            )
            select = Select(dropdown_element)
            options_list = [
                opt.text for opt in select.options if opt.text != default_option_text
            ]
            logger.info(
                f"Successfully fetched {len(options_list)} options from dropdown '{element_id}'."
            )
        except Exception as e:
            logger.error(f"Could not fetch options from dropdown '{element_id}': {e}")
        finally:
            if driver:
                driver.quit()
        return options_list

    def _select_dropdown_option(
        self,
        driver: webdriver.Chrome,
        element_id: str,
        option_text: str,
        max_retries: int = 3,
    ) -> bool:
        """Select option from dropdown with retry logic."""
        for attempt in range(max_retries):
            try:
                dropdown_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, element_id))
                )
                select = Select(dropdown_element)
                select.select_by_visible_text(option_text)
                logger.info(f"Successfully selected '{option_text}' from '{element_id}'.")
                return True
            except StaleElementReferenceException:
                logger.warning(
                    f"Stale element reference on '{element_id}', retrying... (attempt {attempt + 1})"
                )
                time.sleep(1)
                continue
            except NoSuchElementException:
                logger.error(f"Option '{option_text}' not found in dropdown '{element_id}'.")
                return False
            except Exception as e:
                logger.error(f"Error selecting dropdown option: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                continue
        return False

    def _set_date_input(self, driver: webdriver.Chrome, days_back: int = 7) -> bool:
        """Set date input field using JavaScript to avoid calendar popups."""
        try:
            target_date = datetime.now() - timedelta(days=days_back)
            date_string = target_date.strftime("%d-%b-%Y")

            date_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "txtDate"))
            )

            # Use JavaScript to directly set the value, which is faster and more reliable
            driver.execute_script(f"arguments[0].value = '{date_string}';", date_input)

            logger.info(f"Date set to: {date_string}")
            return True
        except Exception as e:
            logger.error(f"Error setting date: {e}")
            return False

    def _click_button(self, driver: webdriver.Chrome, button_id: str) -> bool:
        """Click button with error handling."""
        try:
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, button_id))
            )
            driver.execute_script("arguments[0].click();", button)
            logger.info(f"Button '{button_id}' clicked successfully.")
            return True
        except Exception as e:
            logger.error(f"Error clicking button '{button_id}': {e}")
            return False

    def _extract_table_data(self, driver: webdriver.Chrome) -> List[Dict]:
        """
        Extract data from the results table robustly by parsing HTML cells.
        """
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "cphBody_GridPriceData"))
            )
            soup = BeautifulSoup(driver.page_source, "html.parser")
            table = soup.find(id="cphBody_GridPriceData")
            
            if not table:
                logger.warning("Price data table not found in page source.")
                return []

            rows = table.find_all("tr")
            if len(rows) < 2:  # Header + at least one data row
                logger.warning("No data rows found in the price table.")
                return []

            json_list = []
            # The first row is the header, so we start from the second row
            for row in rows[1:]:
                cells = row.find_all("td")
                if len(cells) < 11:
                    continue  # Skip malformed rows

                try:
                    data_dict = {
                        "S_No": cells[0].text.strip(),
                        "Market_Center": cells[1].text.strip(),
                        "Commodity": cells[3].text.strip(),
                        "Variety": cells[4].text.strip(),
                        "Grade": cells[5].text.strip(),
                        "Min_Price": format_price(cells[6].text.strip()),
                        "Max_Price": format_price(cells[7].text.strip()),
                        "Modal_Price": format_price(cells[8].text.strip()),
                        "Date": cells[9].text.strip(),
                    }

                    # Validate that we have meaningful data before adding
                    if data_dict["Market_Center"] and data_dict["Modal_Price"]:
                        json_list.append(data_dict)
                except IndexError:
                    logger.warning(f"Skipping a row with unexpected cell count.")
                    continue
            
            logger.info(f"Extracted {len(json_list)} records from table.")
            return clean_text_data(json_list) if callable(clean_text_data) else json_list

        except TimeoutException:
            logger.error("Timeout waiting for table data to appear.")
            return []
        except Exception as e:
            logger.error(f"An unexpected error occurred while extracting table data: {e}")
            return []

    def get_available_commodities(self) -> List[str]:
        """
        [LIVE] Scrapes the list of available commodities from the website.
        """
        logger.info("Fetching available commodities from agmarknet.gov.in...")
        return self._get_dropdown_options("ddlCommodity")

    def get_available_states(self) -> List[str]:
        """
        [LIVE] Scrapes the list of available states from the website.
        """
        logger.info("Fetching available states from agmarknet.gov.in...")
        return self._get_dropdown_options("ddlState")

    def get_markets_by_state(self, state: str) -> List[str]:
        """
        [LIVE] Scrapes the list of available markets for a given state.
        This requires selecting the state first to trigger a page update.
        """
        logger.info(f"Fetching markets for state: {state}...")
        driver = self._setup_driver()
        market_list = []
        try:
            driver.get(self.base_url)
            # First, select the state to trigger the update
            if not self._select_dropdown_option(driver, "ddlState", state):
                raise Exception(f"Could not select state '{state}'.")

            # Wait for the market dropdown to be populated.
            # A simple way is to wait for the default "--Select--" option to become stale.
            WebDriverWait(driver, 10).until(
                EC.staleness_of(driver.find_element(By.XPATH, "//select[@id='ddlMarket']/option[1]"))
            )
            
            # Now, get the options from the populated market dropdown
            market_dropdown = Select(WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ddlMarket"))
            ))
            market_list = [opt.text for opt in market_dropdown.options if opt.text != "--Select--"]
            logger.info(f"Found {len(market_list)} markets for {state}.")
        
        except Exception as e:
            logger.error(f"Failed to get markets for '{state}'. Error: {e}")
        finally:
            if driver:
                driver.quit()
        return market_list

    def scrape_market_data(self, commodity: str, state: str, market: str, days: int = 1) -> List[Dict]:
        """
        [LIVE] Scrape market data for a specific commodity, state, and market.
        """
        if not (1 <= days <= getattr(Config, 'MAX_DAYS_BACK', 30)):
            logger.error(f"Days parameter {days} is out of valid range (1-30).")
            return []

        self.driver = None
        try:
            logger.info(f"Starting data extraction for {commodity} in {market}, {state} for day {days} ago.")
            self.driver = self._setup_driver()
            self.driver.get(self.base_url)
            
            # Perform selection sequence
            if not self._select_dropdown_option(self.driver, "ddlCommodity", commodity): return []
            if not self._select_dropdown_option(self.driver, "ddlState", state): return []
            
            # This is crucial: The market dropdown populates only after state selection.
            # A small, explicit wait can be robust here.
            time.sleep(2) 
            
            # Wait for the market dropdown to be ready before selecting
            market_dropdown_element = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "ddlMarket"))
            )
            # Also wait for options to be more than 1 (i.e., not just '--Select--')
            WebDriverWait(self.driver, 15).until(lambda d: len(Select(market_dropdown_element).options) > 1)

            if not self._select_dropdown_option(self.driver, "ddlMarket", market): return []

            if not self._set_date_input(self.driver, days): return []

            # Final "Go" click to fetch the data table
            if not self._click_button(self.driver, "btnGo"): return []

            # Extract data from the resulting table
            data = self._extract_table_data(self.driver)
            log_request(commodity, state, market, len(data) > 0, len(data))
            return data
            
        except Exception as e:
            logger.error(f"An error occurred during scraping: {e}")
            log_request(commodity, state, market, False, 0)
            return []
        finally:
            self.cleanup()
            
    def get_price_trends(self, commodity: str, state: str, market: str, days: int = 7) -> Dict:
        """
        [LIVE] Get price trends by scraping data for each of the last N days.
        Warning: This can be slow as it scrapes each day individually.
        """
        logger.info(f"Calculating price trend for {commodity} in {market}, {state} over the last {days} days.")
        all_prices = []
        dates = []
        
        for day_ago in range(1, days + 1):
            logger.info(f"Fetching data for {day_ago} day(s) ago...")
            daily_data = self.scrape_market_data(commodity, state, market, days=day_ago)
            if daily_data:
                # We will use the first record's modal price for that day for simplicity
                try:
                    modal_price_str = daily_data[0].get("Modal_Price", "0").replace(",", "")
                    modal_price = float(modal_price_str)
                    all_prices.append(modal_price)
                    dates.append(datetime.now() - timedelta(days=day_ago))
                except (ValueError, IndexError) as e:
                    logger.warning(f"Could not parse price for day {day_ago} ago. Data: {daily_data[0]}. Error: {e}")

        if not all_prices:
            logger.warning("No price data found for the given period to calculate trends.")
            return {}

        # Reverse lists to have them in chronological order
        all_prices.reverse()
        dates.reverse()

        # Trend calculation
        trend = "stable"
        percentage_change = 0
        if len(all_prices) > 1:
            price_change = all_prices[-1] - all_prices[0]
            if price_change > 0:
                trend = "upward"
            elif price_change < 0:
                trend = "downward"
            
            if all_prices[0] != 0:
                percentage_change = (price_change / all_prices[0]) * 100

        return {
            "commodity": commodity,
            "state": state,
            "market": market,
            "period": f"Last {days} days",
            "trend_data_points": len(all_prices),
            "highest_price": max(all_prices),
            "lowest_price": min(all_prices),
            "average_price": sum(all_prices) / len(all_prices),
            "latest_price": all_prices[-1],
            "trend": trend,
            "percentage_change": round(percentage_change, 2),
            "last_updated": datetime.now().isoformat(),
        }

    def cleanup(self) -> None:
        """Cleanup resources when done."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver cleaned up successfully.")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
            finally:
                self.driver = None

    def __del__(self) -> None:
        """Cleanup when object is destroyed."""
        self.cleanup()

# --- Example Usage ---
if __name__ == "__main__":
    # Initialize the scraper in non-headless mode to see the browser actions
    scraper = MarketDataScraper(headless=False)

    try:
        # --- 1. Get List of Available States ---
        print("\n--- Fetching available states... ---")
        states = scraper.get_available_states()
        print(f"Found {len(states)} states. First 5: {states[:5]}")

        # --- 2. Get List of Available Commodities ---
        print("\n--- Fetching available commodities... ---")
        commodities = scraper.get_available_commodities()
        print(f"Found {len(commodities)} commodities. First 5: {commodities[:5]}")

        # --- 3. Get Markets for a Specific State ---
        target_state = "Maharashtra"
        print(f"\n--- Fetching markets for {target_state}... ---")
        markets = scraper.get_markets_by_state(target_state)
        print(f"Found {len(markets)} markets in {target_state}. First 5: {markets[:5]}")
        
        # --- 4. Scrape Data for a Specific Market ---
        target_commodity = "Onion"
        target_market = "Pune"
        print(f"\n--- Scraping latest data for {target_commodity} in {target_market}, {target_state}... ---")
        market_data = scraper.scrape_market_data(target_commodity, target_state, target_market, days=1)
        if market_data:
            print(json.dumps(market_data, indent=2))
        else:
            print("No market data found for the latest day.")

        # --- 5. Get Price Trends ---
        print(f"\n--- Calculating price trends for {target_commodity} in {target_market} for the last 5 days... ---")
        # Note: This can be slow! Using a small number of days for the example.
        trends = scraper.get_price_trends(target_commodity, target_state, target_market, days=5)
        if trends:
            print(json.dumps(trends, indent=2))
        else:
            print("Could not calculate price trends.")

    except Exception as e:
        logger.error(f"An error occurred in the main execution block: {e}")
    finally:
        # The scraper's __del__ method will handle cleanup, but it's good practice to do it explicitly.
        scraper.cleanup()
        print("\n--- Script finished ---")