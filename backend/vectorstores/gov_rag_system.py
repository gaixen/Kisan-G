import numpy as np
from typing import List, Dict, Optional, Tuple
import json
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class DocumentSource:
    """Represents a document source with metadata"""
    def __init__(self, url: str, title: str, organization: str, last_updated: str = None):
        self.url = url
        self.title = title
        self.organization = organization
        self.last_updated = last_updated or datetime.now().isoformat()
        self.id = hash(url + title)

class GovernmentRAGSystem:
    """RAG system for government agricultural data retrieval"""
    
    def __init__(self):
        self.documents = []
        self.embeddings = []
        self.sources = {}
        self.initialize_mock_data()
    
    def initialize_mock_data(self):
        """Initialize with mock government scheme data"""
        mock_sources = [
            DocumentSource(
                "https://pmkisan.gov.in/",
                "PM-KISAN Samman Nidhi Yojana",
                "Ministry of Agriculture & Farmers Welfare"
            ),
            DocumentSource(
                "https://pmfby.gov.in/",
                "Pradhan Mantri Fasal Bima Yojana",
                "Ministry of Agriculture & Farmers Welfare"
            ),
            DocumentSource(
                "https://soilhealth.dac.gov.in/",
                "Soil Health Card Scheme",
                "Department of Agriculture & Cooperation"
            ),
            DocumentSource(
                "https://icar.org.in/",
                "ICAR Research Guidelines",
                "Indian Council of Agricultural Research"
            ),
        ]
        
        mock_documents = [
            {
                "content": "PM-KISAN provides direct income support of ₹6000 per year to small farmer families having landholding up to 2 hectares. The scheme aims to supplement financial needs of farmers for agriculture inputs.",
                "source_id": mock_sources[0].id,
                "scheme_id": "pm-kisan",
                "keywords": ["income support", "small farmers", "landholding", "financial assistance"]
            },
            {
                "content": "Pradhan Mantri Fasal Bima Yojana provides insurance coverage for crop losses due to natural calamities, pests & diseases. Premium rates are 2% for kharif crops, 1.5% for rabi crops.",
                "source_id": mock_sources[1].id,
                "scheme_id": "crop-insurance",
                "keywords": ["crop insurance", "natural calamities", "premium rates", "kharif", "rabi"]
            },
            {
                "content": "Soil Health Card provides information on soil nutrient status and recommendations on appropriate dosage of nutrients. Cards are issued every 2 years to all farmers.",
                "source_id": mock_sources[2].id,
                "scheme_id": "soil-health",
                "keywords": ["soil health", "nutrient status", "soil testing", "recommendations"]
            },
            {
                "content": "ICAR promotes agricultural research and education. It provides technical guidelines for crop management, pest control, and sustainable farming practices.",
                "source_id": mock_sources[3].id,
                "scheme_id": "icar-guidelines",
                "keywords": ["agricultural research", "crop management", "pest control", "sustainable farming"]
            }
        ]
        
        # Store sources
        for source in mock_sources:
            self.sources[source.id] = source
        
        # Store documents with mock embeddings
        for i, doc in enumerate(mock_documents):
            self.documents.append(doc)
            # Mock embedding - in real implementation, use proper embedding model
            self.embeddings.append(np.random.rand(128).tolist())
    
    def search_schemes(self, query: str, user_profile: Dict = None) -> List[Dict]:
        """
        Search for relevant schemes based on query and user profile
        
        Args:
            query: Search query
            user_profile: User information for personalized results
            
        Returns:
            List of matching schemes with source attribution
        """
        try:
            # Simple keyword-based matching for demonstration
            query_lower = query.lower()
            relevant_docs = []
            
            for doc in self.documents:
                # Check if query matches keywords or content
                if any(keyword in query_lower for keyword in doc['keywords']) or \
                   query_lower in doc['content'].lower():
                    
                    source = self.sources[doc['source_id']]
                    scheme_info = {
                        "scheme_id": doc['scheme_id'],
                        "content": doc['content'],
                        "relevance_score": 0.85,  # Mock relevance score
                        "source": {
                            "title": source.title,
                            "url": source.url,
                            "organization": source.organization,
                            "last_updated": source.last_updated
                        },
                        "keywords": doc['keywords']
                    }
                    
                    # Add eligibility check if user profile provided
                    if user_profile:
                        scheme_info['eligible'] = self._check_eligibility(
                            doc['scheme_id'], user_profile
                        )
                    
                    relevant_docs.append(scheme_info)
            
            # Sort by relevance score
            relevant_docs.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            logger.info(f"Found {len(relevant_docs)} relevant schemes for query: {query}")
            return relevant_docs
            
        except Exception as e:
            logger.error(f"Error searching schemes: {str(e)}")
            return []
    
    def _check_eligibility(self, scheme_id: str, user_profile: Dict) -> bool:
        """
        Check if user is eligible for a scheme
        
        Args:
            scheme_id: Scheme identifier
            user_profile: User information
            
        Returns:
            Boolean indicating eligibility
        """
        # Mock eligibility logic
        land_size = user_profile.get('land_size_hectares', 0)
        crop_type = user_profile.get('primary_crop', '')
        
        eligibility_rules = {
            'pm-kisan': land_size <= 2,
            'crop-insurance': crop_type in ['wheat', 'rice', 'cotton', 'sugarcane'],
            'soil-health': True,  # All farmers eligible
            'icar-guidelines': True  # All farmers eligible
        }
        
        return eligibility_rules.get(scheme_id, False)
    
    def get_scheme_details(self, scheme_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific scheme
        
        Args:
            scheme_id: Scheme identifier
            
        Returns:
            Detailed scheme information with sources
        """
        try:
            scheme_doc = next(
                (doc for doc in self.documents if doc['scheme_id'] == scheme_id),
                None
            )
            
            if not scheme_doc:
                return None
            
            source = self.sources[scheme_doc['source_id']]
            
            return {
                "scheme_id": scheme_id,
                "content": scheme_doc['content'],
                "source": {
                    "title": source.title,
                    "url": source.url,
                    "organization": source.organization,
                    "last_updated": source.last_updated
                },
                "keywords": scheme_doc['keywords'],
                "detailed_info": self._get_detailed_scheme_info(scheme_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting scheme details: {str(e)}")
            return None
    
    def _get_detailed_scheme_info(self, scheme_id: str) -> Dict:
        """Get additional detailed information for schemes"""
        details = {
            'pm-kisan': {
                'benefits': '₹6000 per year in 3 installments',
                'application_process': 'Online through PM-KISAN portal or Common Service Centers',
                'required_documents': ['Aadhaar Card', 'Bank Account Details', 'Land Records'],
                'timeline': 'Installments released every 4 months'
            },
            'crop-insurance': {
                'benefits': 'Coverage up to sum insured for crop losses',
                'application_process': 'Through banks, insurance companies, or online portal',
                'required_documents': ['Aadhaar Card', 'Bank Account', 'Land Records', 'Sowing Certificate'],
                'timeline': 'Apply before cut-off dates for each season'
            },
            'soil-health': {
                'benefits': 'Free soil testing and nutrient recommendations',
                'application_process': 'Through local agriculture office or soil testing centers',
                'required_documents': ['Land Records', 'Farmer ID'],
                'timeline': 'Cards issued every 2 years'
            }
        }
        
        return details.get(scheme_id, {})
    
    def add_document(self, content: str, source: DocumentSource, scheme_id: str, keywords: List[str]):
        """
        Add a new document to the RAG system
        
        Args:
            content: Document content
            source: Source information
            scheme_id: Associated scheme ID
            keywords: Relevant keywords
        """
        try:
            # Store source if not exists
            if source.id not in self.sources:
                self.sources[source.id] = source
            
            # Add document
            doc = {
                "content": content,
                "source_id": source.id,
                "scheme_id": scheme_id,
                "keywords": keywords
            }
            
            self.documents.append(doc)
            # In real implementation, generate proper embeddings
            self.embeddings.append(np.random.rand(128).tolist())
            
            logger.info(f"Added document for scheme: {scheme_id}")
            
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
    
    def scrape_government_websites(self) -> List[Dict]:
        """
        Scrape government websites for latest scheme information
        This is a placeholder for actual web scraping implementation
        """
        try:
            # Mock scraping results
            scraped_data = [
                {
                    "url": "https://pmkisan.gov.in/",
                    "title": "PM-KISAN Updates",
                    "content": "Latest updates on PM-KISAN scheme implementation and beneficiary registration.",
                    "last_scraped": datetime.now().isoformat()
                }
            ]
            
            logger.info(f"Scraped {len(scraped_data)} government websites")
            return scraped_data
            
        except Exception as e:
            logger.error(f"Error scraping government websites: {str(e)}")
            return []
