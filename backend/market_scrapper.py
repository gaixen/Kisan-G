import time, json, logging, os, sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException)
from bs4 import BeautifulSoup

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Fallback Functions and Config (if an external API is not available) ---
def format_price(price): return price
def clean_text_data(data): return data
def log_request(c, s, m, success, rc=0): pass
class Config:
    SCRAPER_HEADLESS = True
    SCRAPER_TIMEOUT = 25

class MarketDataScraper:
    """
    A robust web scraper for agmarknet.gov.in, built to handle dynamic page updates.
    """
    def __init__(self, base_url: str = "https://agmarknet.gov.in/SearchCmmMkt.aspx", headless: bool = True, timeout: int = 25):
        self.base_url = base_url
        self.headless = headless if headless is not None else getattr(Config, 'SCRAPER_HEADLESS', True)
        self.timeout = timeout if timeout is not None else getattr(Config, 'SCRAPER_TIMEOUT', 25)

    def _setup_driver(self) -> webdriver.Chrome:
        """Initializes the Selenium WebDriver with optimized options."""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(self.timeout)
            return driver
        except WebDriverException as e:
            logger.error(f"Failed to setup Chrome driver. Ensure chromedriver is in your PATH. Error: {e}")
            raise

    def _select_dropdown_option(self, driver: webdriver.Chrome, element_id: str, option_text: str) -> bool:
        """Selects an option from a dropdown, re-finding the element to avoid staleness."""
        try:
            select_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, element_id)))
            Select(select_element).select_by_visible_text(option_text)
            logger.debug(f"Successfully selected '{option_text}' from '{element_id}'.")
            return True
        except (NoSuchElementException, TimeoutException):
            logger.error(f"Option '{option_text}' not found or dropdown '{element_id}' not available.")
            return False

    def _set_date_input(self, driver: webdriver.Chrome, days_back: int) -> bool:
        """Sets the date input field."""
        date_string = (datetime.now() - timedelta(days=days_back)).strftime('%d-%b-%Y')
        try:
            date_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "txtDate")))
            driver.execute_script(f"arguments[0].value = '{date_string}';", date_input)
            return True
        except TimeoutException:
            logger.error("Could not find the date input field.")
            return False

    def _click_button(self, driver: webdriver.Chrome, button_id: str) -> bool:
        """Clicks a button."""
        try:
            button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, button_id)))
            driver.execute_script("arguments[0].click();", button)
            return True
        except TimeoutException:
            logger.error(f"Could not click button '{button_id}'.")
            return False

    def _extract_table_data(self, driver: webdriver.Chrome) -> List[Dict]:
        """Extracts data from the results table."""
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "cphBody_GridPriceData")))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            table = soup.find(id="cphBody_GridPriceData")
            
            if not table or len(table.find_all("tr")) <= 1:
                return []

            json_list = []
            for row in table.find_all("tr")[1:]:
                cells = row.find_all("td")
                if len(cells) < 10: continue
                data_dict = {
                    "Market_Center": cells[1].text.strip(), "Commodity": cells[3].text.strip(),
                    "Min_Price": format_price(cells[6].text.strip()), "Max_Price": format_price(cells[7].text.strip()),
                    "Modal_Price": format_price(cells[8].text.strip()), "Date": cells[9].text.strip(),
                }
                if data_dict["Market_Center"] and data_dict["Modal_Price"]:
                    json_list.append(data_dict)
            
            if json_list:
                logger.info(f"Extracted {len(json_list)} records for date {json_list[0].get('Date', 'N/A')}.")
            return clean_text_data(json_list)
        except TimeoutException:
            logger.debug("No data table found on page for the selected criteria.")
            return []

    def scrape_market_data(self, commodity: str, state: str, market: str, days_back: int = 1) -> Optional[List[Dict]]:
        """
        [IMPROVED] Scrapes market data for a single day with a retry mechanism for stability.
        """
        MAX_ATTEMPTS = 3
        for attempt in range(MAX_ATTEMPTS):
            driver = None
            try:
                driver = self._setup_driver()
                driver.get(self.base_url)

                if not self._select_dropdown_option(driver, "ddlCommodity", commodity): return None
                if not self._select_dropdown_option(driver, "ddlState", state): return None
                
                # Crucial Wait: After selecting the state, wait for the market list to be reloaded.
                WebDriverWait(driver, 15).until(lambda d: len(Select(d.find_element(By.ID, "ddlMarket")).options) > 1)
                
                if not self._select_dropdown_option(driver, "ddlMarket", market): return None
                if not self._set_date_input(driver, days_back): return None
                if not self._click_button(driver, "btnGo"): return None
                
                data = self._extract_table_data(driver)
                log_request(commodity, state, market, success=True, rc=len(data))
                return data # Success, exit the loop and return data

            except StaleElementReferenceException:
                logger.warning(f"StaleElementReferenceException on attempt {attempt + 1}/{MAX_ATTEMPTS}. Retrying...")
                time.sleep(2) # Wait a moment before retrying
                continue # Go to the next attempt in the loop

            except Exception as e:
                logger.error(f"A critical, non-stale error occurred during scraping: {e}", exc_info=True)
                return None # Fail fast on other errors like Timeout or NoSuchElement

            finally:
                if driver:
                    driver.quit()
        
        logger.error(f"Failed to scrape data after {MAX_ATTEMPTS} attempts due to repeated stale element errors.")
        return None # Return None if all attempts fail

    # --- Other methods like find_most_recent_market_data, get_price_trends, etc. ---
    # These methods use scrape_market_data and will now benefit from its new stability.
    def find_most_recent_market_data(self, commodity: str, state: str, market: str, max_days_to_check: int = 14) -> List[Dict]:
        """
        [ROBUST] Searches backwards day-by-day to find the most recent available data.
        """
        logger.info(f"Starting robust search for '{commodity}' in '{market}, {state}' (checking last {max_days_to_check} days).")
        for days in range(1, max_days_to_check + 1):
            logger.info(f"--> Checking for data {days} day(s) ago...")
            data = self.scrape_market_data(commodity, state, market, days_back=days)
            
            if data is None: # Critical error occurred
                logger.error("Stopping search due to a critical scraping error.")
                return []
            if data: # Data found
                logger.info(f"Success! Found most recent data from {days} day(s) ago.")
                return data
        
        logger.warning(f"No data found for '{commodity}' in '{market}, {state}' within the last {max_days_to_check} days.")
        return []

    def get_price_trends(self, commodity: str, state: str, market: str, days: int = 7) -> Dict:
        """
        [LIVE] Calculates price trends by scraping data for each of the last N days.
        """
        logger.info(f"Calculating price trend for '{commodity}' in '{market}' over the last {days} days.")
        prices = []
        
        for day_ago in range(days, 0, -1):
            data = self.scrape_market_data(commodity, state, market, days_back=day_ago)
            if data:
                try:
                    prices.append(float(data[0].get("Modal_Price", "0").replace(",", "")))
                except (ValueError, IndexError):
                    continue
        
        if not prices: return {}

        trend, p_change = "stable", 0.0
        if len(prices) > 1 and prices[0] != 0:
            price_change = prices[-1] - prices[0]
            if price_change > 0: trend = "upward"
            elif price_change < 0: trend = "downward"
            p_change = (price_change / prices[0]) * 100

        return {
            "commodity": commodity, "market": market, "period_days": days,
            "data_points_found": len(prices), "highest_price": max(prices), "lowest_price": min(prices),
            "average_price": round(sum(prices) / len(prices), 2), "latest_price": prices[-1],
            "trend": trend, "percentage_change": round(p_change, 2),
        }

# --- Example Usage ---
if __name__ == "__main__":
    scraper = MarketDataScraper(headless=True) # Set to False to watch the browser

    try:
        target_state = "Maharashtra"
        target_market = "Pune"
        target_commodity = "Onion"
        
        print(f"\n--- Finding most recent data for {target_commodity} in {target_market}... ---")
        market_data = scraper.find_most_recent_market_data(
            commodity=target_commodity,
            state=target_state,
            market=target_market,
            max_days_to_check=7
        )
        if market_data:
            print(json.dumps(market_data, indent=2))
        else:
            print("--> No recent data found.")

        print(f"\n--- Calculating price trends for a different commodity, 'Potato'... ---")
        trends = scraper.get_price_trends(
            commodity="Potato", 
            state=target_state, 
            market=target_market, 
            days=5
        )
        if trends:
            print(json.dumps(trends, indent=2))
        else:
            print("--> Could not calculate price trends.")

    except Exception as e:
        logger.error(f"An error occurred in the main execution block: {e}")
    finally:
        print("\n--- Script finished ---")
        
        
        
        
        
