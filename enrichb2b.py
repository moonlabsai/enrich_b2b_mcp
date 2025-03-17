"""
EnrichB2B API Client

This module provides a Python client for the EnrichB2B API, which validates whether a lead
still works at a company with real-time lookups against their LinkedIn profile and returns
a validation score.

The API provides endpoints to search leads and companies on LinkedIn and get fresh data.
Both single and bulk endpoints are available to fit various business needs.
"""

import json
import requests
from typing import Dict, List, Optional, Union, Any
from dotenv import load_dotenv
import os
import random

load_dotenv()

ENRICHB2B_API_KEY = os.getenv("ENRICHB2B_API_KEY")
class EnrichB2BConfig:
    """Configuration for EnrichB2B API client."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.enrichb2bdata.com"):
        """
        Initialize EnrichB2B configuration.
        
        Args:
            api_key: Your EnrichB2B API key
            base_url: The base URL for the API (defaults to https://api.enrichb2bdata.com)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        
    def get_headers(self) -> Dict[str, str]:
        """Get headers required for API requests."""
        return {
            "X-EB2B-API-Key": self.api_key,
            "Content-Type": "application/json"
        }


class ContactRequest:
    """Represents a request to search for a contact on LinkedIn."""
    
    def __init__(
        self, 
        request_id: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        company: Optional[str] = None,
        job_title: Optional[str] = None
    ):
        """
        Initialize a contact search request.
        
        Args:
            request_id: Optional ID to track this request
            linkedin_url: LinkedIn profile URL of the contact
            first_name: First name of the contact (required if linkedin_url not provided)
            last_name: Last name of the contact (required if linkedin_url not provided)
            company: Company name where the contact works (required if linkedin_url not provided)
            job_title: Job title of the contact (optional, but improves search accuracy)
        """
        self.request_id = request_id
        self.linkedin_url = linkedin_url
        self.first_name = first_name
        self.last_name = last_name
        self.company = company
        self.job_title = job_title
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary for API submission."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


class CompanyRequest:
    """Represents a request to search for a company on LinkedIn."""
    
    def __init__(
        self,
        request_id: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        name: Optional[str] = None
    ):
        """
        Initialize a company search request.
        
        Args:
            request_id: Optional ID to track this request
            linkedin_url: LinkedIn URL of the company
            name: Name of the company
        """
        self.request_id = request_id
        self.linkedin_url = linkedin_url
        self.name = name
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary for API submission."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


class CompanyEmployeeRequest:
    """Represents a request to search for employees of a company."""
    
    def __init__(
        self,
        company_linkedin_url: str,
        search_name: Optional[str] = None,
        page_size: int = 50,
        offset: int = 0
    ):
        """
        Initialize a company employees search request.
        
        Args:
            company_linkedin_url: LinkedIn URL of the company (required)
            search_name: Optional name to track this search
            page_size: Number of results per page (10-50)
            offset: Offset for pagination (starts at 0)
        """
        self.company_linkedin_url = company_linkedin_url
        self.search_name = search_name
        self.page_size = min(max(page_size, 10), 50)  # Ensure between 10-50
        self.offset = max(offset, 0)  # Ensure non-negative
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary for API submission."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


class ContactActivitiesRequest:
    """Represents a request to search for activities of a contact."""
    
    def __init__(
        self,
        linkedin_url: str,
        request_id: Optional[str] = None,
        linkedin_profile_uid: Optional[str] = None,
        search_name: Optional[str] = None,
        how_many_pages: int = 1,
        how_many_pages_comments_per_post: Optional[int] = None,
        how_many_pages_likes_per_post: Optional[int] = None
    ):
        """
        Initialize a contact activities search request.
        
        Args:
            linkedin_url: LinkedIn URL of the contact (required)
            request_id: Optional ID to track this request
            linkedin_profile_uid: Contact UID on LinkedIn
            search_name: Optional name to track this search
            how_many_pages: Number of pages to fetch (1-50)
            how_many_pages_comments_per_post: Pages of comments to fetch per post (0-50)
            how_many_pages_likes_per_post: Pages of likes to fetch per post (0-50)
        """
        self.linkedin_url = linkedin_url
        # Generate a random 8-digit request ID if none provided
        self.request_id = request_id if request_id else str(random.randint(10000000, 99999999))
        self.linkedin_profile_uid = linkedin_profile_uid
        self.search_name = search_name
        self.how_many_pages = min(max(how_many_pages, 1), 50)  # Ensure between 1-50
        
        if how_many_pages_comments_per_post is not None:
            self.how_many_pages_comments_per_post = min(max(how_many_pages_comments_per_post, 0), 50)
        else:
            self.how_many_pages_comments_per_post = None
            
        if how_many_pages_likes_per_post is not None:
            self.how_many_pages_likes_per_post = min(max(how_many_pages_likes_per_post, 0), 50)
        else:
            self.how_many_pages_likes_per_post = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary for API submission."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


class EnrichB2BClient:
    """Client for the EnrichB2B API."""
    
    def __init__(self, config: EnrichB2BConfig):
        """
        Initialize the EnrichB2B API client.
        
        Args:
            config: Configuration object with API key and base URL
        """
        self.config = config
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Make a request to the EnrichB2B API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data (for POST requests)
            
        Returns:
            Dict: API response as a dictionary
            
        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If the response is not valid JSON
        """
        url = f"{self.config.base_url}{endpoint}"
        headers = self.config.get_headers()
        
        response = requests.request(method, url, headers=headers, json=data)
        
        # Raise exception for HTTP errors
        response.raise_for_status()
        
        return response.json()
    
    # Contact endpoints
    
    def search_contact(
        self, 
        request: ContactRequest,
        extended_search: Optional[bool] = None,
        include_company_details: Optional[bool] = None,
        include_followers_count: Optional[bool] = None,
        search_name: Optional[str] = None
    ) -> Dict:
        """
        Search for a contact on LinkedIn.
        
        Args:
            request: Contact search request
            extended_search: Whether to use extended search
            include_company_details: Whether to include company details
            include_followers_count: Whether to include followers count
            search_name: Optional name to track this search
            
        Returns:
            Dict: API response
        """
        data = {
            **request.to_dict()
        }
        
        if extended_search is not None:
            data["extended_search"] = extended_search
        if include_company_details is not None:
            data["include_company_details"] = include_company_details
        if include_followers_count is not None:
            data["include_followers_count"] = include_followers_count
        if search_name is not None:
            data["search_name"] = search_name
            
        return self._make_request("POST", "/v1/search/contact", data)
    
    def search_contact_bulk(
        self, 
        requests: List[ContactRequest],
        extended_search: Optional[bool] = None,
        include_company_details: Optional[bool] = None,
        include_followers_count: Optional[bool] = None,
        search_name: Optional[str] = None
    ) -> Dict:
        """
        Search for multiple contacts on LinkedIn in bulk.
        
        Args:
            requests: List of contact search requests
            extended_search: Whether to use extended search
            include_company_details: Whether to include company details
            include_followers_count: Whether to include followers count
            search_name: Optional name to track this search
            
        Returns:
            Dict: API response
        """
        data = {
            "request": [req.to_dict() for req in requests]
        }
        
        if extended_search is not None:
            data["extended_search"] = extended_search
        if include_company_details is not None:
            data["include_company_details"] = include_company_details
        if include_followers_count is not None:
            data["include_followers_count"] = include_followers_count
        if search_name is not None:
            data["search_name"] = search_name
            
        return self._make_request("POST", "/v1/search/contact/bulk", data)
    
    # Company endpoints
    
    def search_company(
        self, 
        request: CompanyRequest,
        extended_search: Optional[bool] = None,
        search_name: Optional[str] = None
    ) -> Dict:
        """
        Search for a company on LinkedIn.
        
        Args:
            request: Company search request
            extended_search: Whether to use extended search
            search_name: Optional name to track this search
            
        Returns:
            Dict: API response
        """
        data = {
            **request.to_dict()
        }
        
        if extended_search is not None:
            data["extended_search"] = extended_search
        if search_name is not None:
            data["search_name"] = search_name
            
        return self._make_request("POST", "/v1/search/company", data)
    
    def search_company_bulk(
        self, 
        requests: List[CompanyRequest],
        extended_search: Optional[bool] = None,
        search_name: Optional[str] = None
    ) -> Dict:
        """
        Search for multiple companies on LinkedIn in bulk.
        
        Args:
            requests: List of company search requests
            extended_search: Whether to use extended search
            search_name: Optional name to track this search
            
        Returns:
            Dict: API response
        """
        data = {
            "request": [req.to_dict() for req in requests]
        }
        
        if extended_search is not None:
            data["extended_search"] = extended_search
        if search_name is not None:
            data["search_name"] = search_name
            
        return self._make_request("POST", "/v1/search/company/bulk", data)
    
    def search_company_employees(self, request: CompanyEmployeeRequest) -> Dict:
        """
        Search for employees of a company on LinkedIn.
        
        Args:
            request: Company employees search request
            
        Returns:
            Dict: API response
        """
        return self._make_request("POST", "/v1/search/company_employees", request.to_dict())
    
    # Contact activities endpoints
    
    def search_contact_activities(self, request: ContactActivitiesRequest) -> Dict:
        """
        Search for activities of a contact on LinkedIn.
        
        Args:
            request: Contact activities search request
            
        Returns:
            Dict: API response
        """
        return self._make_request("POST", "/v1/search/contact/activities", request.to_dict())
    
    def search_contact_activities_bulk(
        self, 
        requests: List[ContactActivitiesRequest],
        how_many_pages: int = 1,
        how_many_pages_comments_per_post: Optional[int] = None,
        how_many_pages_likes_per_post: Optional[int] = None,
        search_name: Optional[str] = None
    ) -> Dict:
        """
        Search for activities of multiple contacts on LinkedIn in bulk.
        
        Args:
            requests: List of contact post requests
            how_many_pages: Number of pages to fetch (1-10)
            how_many_pages_comments_per_post: Pages of comments to fetch per post (0-50)
            how_many_pages_likes_per_post: Pages of likes to fetch per post (0-50)
            search_name: Optional name to track this search
            
        Returns:
            Dict: API response
        """
        data = {
            "request": [
                {
                    "linkedin_url": req.linkedin_url,
                    "request_id": req.request_id,
                    "linkedin_profile_uid": req.linkedin_profile_uid
                } for req in requests
            ],
            "how_many_pages": min(max(how_many_pages, 1), 10)  # Ensure between 1-10
        }
        
        if how_many_pages_comments_per_post is not None:
            data["how_many_pages_comments_per_post"] = min(max(how_many_pages_comments_per_post, 0), 50)
        
        if how_many_pages_likes_per_post is not None:
            data["how_many_pages_likes_per_post"] = min(max(how_many_pages_likes_per_post, 0), 50)
            
        if search_name is not None:
            data["search_name"] = search_name
            
        return self._make_request("POST", "/v1/search/contact/activities/bulk", data)
    
    def get_post_interactions(
        self, 
        activity_id: str, 
        fetch_type: str,
        page: int = 1,
        limit: int = 10
    ) -> Dict:
        """
        Get interactions on a post.
        
        Args:
            activity_id: ID of the activity (post)
            fetch_type: Type of interactions to fetch (comments, likers, empathy, 
                        entertainment, praise, interest, maybe, funny)
            page: Page number (default 1)
            limit: Number of results per page (default 10)
            
        Returns:
            Dict: API response
        """
        params = {
            "activity_id": activity_id,
            "fetch_type": fetch_type,
            "page": page,
            "limit": limit
        }
        
        # Convert params to query string manually
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        endpoint = f"/v1/search/contact/activities/post-interactions?{query_string}"
        
        return self._make_request("GET", endpoint)
    
    def get_profile_comments(
        self, 
        profile_id: str,
        next_page_token: Optional[str] = None,
        limit: int = 10
    ) -> Dict:
        """
        Get comments on a profile.
        
        Args:
            profile_id: ID of the profile
            next_page_token: Token for pagination
            limit: Number of results per page (default 10)
            
        Returns:
            Dict: API response
        """
        params = {
            "profile_id": profile_id,
            "limit": limit
        }
        
        if next_page_token:
            params["next_page_token"] = next_page_token
        
        # Convert params to query string manually
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        endpoint = f"/v1/search/contact/activities/profile-comments?{query_string}"
        
        return self._make_request("GET", endpoint)


# Usage examples

def example_usage():
    """Example usage of the EnrichB2B API client."""
    
    # Initialize the client
    config = EnrichB2BConfig(ENRICHB2B_API_KEY)
    client = EnrichB2BClient(config)
    
    # # Example 1: Search for a contact by LinkedIn URL
    # contact_req = ContactRequest(
    #     linkedin_url="https://www.linkedin.com/in/davidstubbss"
    # )
    # contact_result = client.search_contact(contact_req)
    # print("Contact search result:", json.dumps(contact_result, indent=2))
    
    # Example 4: Search for activities of a contact
    activities_req = ContactActivitiesRequest(
        linkedin_url="https://www.linkedin.com/in/davidstubbss",
        how_many_pages=1,
        how_many_pages_comments_per_post=1
    )
    activities_result = client.search_contact_activities(activities_req)
    print("Contact activities result:", json.dumps(activities_result, indent=2))