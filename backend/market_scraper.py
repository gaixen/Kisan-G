import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MarketDataScraper:
    def __init__(self, base_url: str = "https://agmarknet.gov.in/SearchCmmMkt.aspx"):
        """
        Initialize the market data scraper
        Args:
            base_url: Base URL for the agmarknet website
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def scrape_market_data(self, commodity: str, state: str, market: str, days: int = 7) -> List[Dict]:
        """
        Scrape market data for a specific commodity, state, and market
        
        Args:
            commodity: Name of the commodity
            state: State name
            market: Market/City name
            days: Number of days back to fetch data
            
        Returns:
            List of dictionaries containing market data
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Mock data for demonstration - replace with actual scraping logic
            mock_data = [
                {
                    "date": (end_date - timedelta(days=i)).strftime("%Y-%m-%d"),
                    "commodity": commodity,
                    "state": state,
                    "market": market,
                    "min_price": 2000 + (i * 10),
                    "max_price": 2500 + (i * 15),
                    "modal_price": 2250 + (i * 12),
                    "arrivals": 100 + (i * 5),
                    "unit": "Quintal"
                }
                for i in range(days)
            ]
            
            logger.info(f"Successfully scraped {len(mock_data)} records for {commodity} in {market}, {state}")
            return mock_data
            
        except Exception as e:
            logger.error(f"Error scraping market data: {str(e)}")
            return []

    def get_available_commodities(self) -> List[str]:
        """
        Get list of available commodities
        
        Returns:
            List of commodity names
        """
        # Mock data - replace with actual scraping
        return [
            "Wheat", "Rice", "Maize", "Barley", "Gram", "Tur (Arhar)", 
            "Masoor", "Moong", "Urad", "Groundnut", "Sunflower", "Soyabean",
            "Rapeseed & Mustard", "Sesamum", "Safflower", "Nigerseed",
            "Cotton", "Jute", "Sugarcane", "Potato", "Onion", "Tomato"
        ]

    def get_available_states(self) -> List[str]:
        """
        Get list of available states
        
        Returns:
            List of state names
        """
        # Mock data - replace with actual scraping
        return [
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
            "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
            "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
            "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
            "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
        ]

    def get_markets_by_state(self, state: str) -> List[str]:
        """
        Get list of markets for a specific state
        
        Args:
            state: State name
            
        Returns:
            List of market names
        """
        # Mock data based on state - replace with actual scraping
        market_mapping = {
            "Karnataka": ["Bangalore", "Mysore", "Hubli", "Mangalore", "Belgaum"],
            "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],
            "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli"],
            "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar"],
            "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda"]
        }
        
        return market_mapping.get(state, ["Default Market"])

    def get_price_trends(self, commodity: str, days: int = 30) -> Dict:
        """
        Get price trends for a commodity over specified days
        
        Args:
            commodity: Name of the commodity
            days: Number of days for trend analysis
            
        Returns:
            Dictionary containing trend data
        """
        try:
            # Mock trend calculation
            base_price = 2200
            trend_data = {
                "commodity": commodity,
                "period": f"Last {days} days",
                "current_price": base_price,
                "highest_price": base_price + 200,
                "lowest_price": base_price - 150,
                "average_price": base_price + 25,
                "trend": "upward",  # upward, downward, stable
                "percentage_change": 5.2,
                "last_updated": datetime.now().isoformat()
            }
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Error calculating price trends: {str(e)}")
            return {}

    def filter_data(self, data: List[Dict], filters: Dict) -> List[Dict]:
        """
        Apply filters to the scraped data
        
        Args:
            data: List of data dictionaries
            filters: Dictionary containing filter criteria
            
        Returns:
            Filtered data
        """
        filtered_data = data.copy()
        
        if 'min_price_range' in filters:
            filtered_data = [
                item for item in filtered_data 
                if item.get('min_price', 0) >= filters['min_price_range']
            ]
        
        if 'max_price_range' in filters:
            filtered_data = [
                item for item in filtered_data 
                if item.get('max_price', 0) <= filters['max_price_range']
            ]
        
        if 'date_from' in filters:
            date_from = datetime.strptime(filters['date_from'], "%Y-%m-%d")
            filtered_data = [
                item for item in filtered_data 
                if datetime.strptime(item.get('date', ''), "%Y-%m-%d") >= date_from
            ]
        
        if 'date_to' in filters:
            date_to = datetime.strptime(filters['date_to'], "%Y-%m-%d")
            filtered_data = [
                item for item in filtered_data 
                if datetime.strptime(item.get('date', ''), "%Y-%m-%d") <= date_to
            ]
        
        return filtered_data
