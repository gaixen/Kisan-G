import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from utils.logging import get_logger, log_exception, log_execution_time

logger = get_logger(__name__)

class DatabaseManager:
    def __init__(self, db_name: str = "kisan_app.db"):
        # Get the absolute path to the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Join the script directory with the database name
        self.db_path = os.path.join(script_dir, db_name)
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Market trends table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                commodity TEXT NOT NULL,
                state TEXT NOT NULL,
                market TEXT NOT NULL,
                latest_price REAL,
                trend TEXT,
                percentage_change REAL,
                data_points_found INTEGER,
                average_price REAL,
                highest_price REAL,
                lowest_price REAL,
                prices_data TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Government schemes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS govt_schemes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                schemes_data TEXT NOT NULL,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Weather data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                weather_info TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Soil analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS soil_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                soil_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crop analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crop_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                query TEXT,
                analysis_result TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Request logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                parameters TEXT,
                response_status INTEGER,
                response_data TEXT,
                execution_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully!")
    
    @log_exception()
    @log_execution_time()
    def log_request(self, endpoint: str, method: str, parameters: Dict = None, 
                   response_status: int = 200, response_data: Any = None, execution_time: float = 0):
        """Log API request details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO request_logs (endpoint, method, parameters, response_status, response_data, execution_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            endpoint,
            method,
            json.dumps(parameters) if parameters else None,
            response_status,
            json.dumps(response_data) if response_data else None,
            execution_time
        ))
        
        conn.commit()
        conn.close()
    
    @log_exception()
    @log_execution_time()
    def store_market_trends(self, commodity: str, state: str, market: str, trends_data: Dict):
        """Store market trends data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO market_trends (
                commodity, state, market, latest_price, trend, percentage_change,
                data_points_found, average_price, highest_price, lowest_price,
                prices_data, message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            commodity, state, market,
            trends_data.get('latest_price'),
            trends_data.get('trend'),
            trends_data.get('percentage_change'),
            trends_data.get('data_points_found'),
            trends_data.get('average_price'),
            trends_data.get('highest_price'),
            trends_data.get('lowest_price'),
            json.dumps(trends_data.get('prices', [])),
            trends_data.get('message')
        ))
        
        conn.commit()
        conn.close()
    
    @log_exception()
    @log_execution_time()
    def get_market_trends(self, commodity: str, state: str, market: str) -> Optional[Dict]:
        """Get stored market trends data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM market_trends 
            WHERE commodity = ? AND state = ? AND market = ?
            ORDER BY created_at DESC LIMIT 1
        ''', (commodity, state, market))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'commodity': row[1],
                'state': row[2],
                'market': row[3],
                'latest_price': row[4],
                'trend': row[5],
                'percentage_change': row[6],
                'data_points_found': row[7],
                'average_price': row[8],
                'highest_price': row[9],
                'lowest_price': row[10],
                'prices': json.loads(row[11]) if row[11] else [],
                'message': row[12]
            }
        return None
    
    @log_exception()
    @log_execution_time()
    def store_govt_schemes(self, query: str, schemes_data: List[Dict], message: str = None):
        """Store government schemes data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO govt_schemes (query, schemes_data, message)
            VALUES (?, ?, ?)
        ''', (query, json.dumps(schemes_data), message))
        
        conn.commit()
        conn.close()
    
    @log_exception()
    @log_execution_time()
    def get_govt_schemes(self, query: str) -> Optional[Dict]:
        """Get stored government schemes data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM govt_schemes 
            WHERE query = ?
            ORDER BY created_at DESC LIMIT 1
        ''', (query,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'schemes': json.loads(row[2]),
                'message': row[3]
            }
        return None
    
    @log_exception()
    @log_execution_time()
    def store_weather_data(self, latitude: float, longitude: float, weather_info: Dict):
        """Store weather data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO weather_data (latitude, longitude, weather_info)
            VALUES (?, ?, ?)
        ''', (latitude, longitude, json.dumps(weather_info)))
        
        conn.commit()
        conn.close()

    
    @log_exception()
    @log_execution_time()
    def store_soil_analysis(self, latitude: float, longitude: float, soil_data: Dict):
        """Store soil analysis data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO soil_analysis (latitude, longitude, soil_data)
            VALUES (?, ?, ?)
        ''', (latitude, longitude, json.dumps(soil_data)))
        
        conn.commit()
        conn.close()
    
    @log_exception()
    @log_execution_time()
    def store_crop_analysis(self, filename: str, query: str, analysis_result: Dict):
        """Store crop analysis result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO crop_analysis (filename, query, analysis_result)
            VALUES (?, ?, ?)
        ''', (filename, query, json.dumps(analysis_result)))
        
        conn.commit()
        conn.close()
    
    @log_exception()
    @log_execution_time()
    def get_request_stats(self) -> Dict:
        """Get request statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT endpoint, COUNT(*) FROM request_logs GROUP BY endpoint')
        endpoint_stats = dict(cursor.fetchall())
        
        cursor.execute('SELECT COUNT(*) FROM request_logs WHERE DATE(created_at) = DATE("now")')
        today_requests = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(execution_time) FROM request_logs')
        avg_response_time = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'endpoint_stats': endpoint_stats,
            'today_requests': today_requests,
            'avg_response_time': round(avg_response_time, 3)
        }
