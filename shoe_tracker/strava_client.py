"""Strava API client for fetching activity data."""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
from stravalib import Client
from stravalib.strava_model import SummaryActivity, DetailedActivity


class StravaClient:
    """Client for interacting with the Strava API."""
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the Strava client.
        
        Args:
            access_token: Strava API access token. If not provided, will try to get from environment.
        """
        self.access_token = access_token or os.getenv('STRAVA_ACCESS_TOKEN')
        self.client = Client()
        if self.access_token:
            self.client.access_token = self.access_token
    
    def authorize(self, client_id: int, client_secret: str, code: str) -> Dict[str, str]:
        """
        Exchange authorization code for access token.
        
        Args:
            client_id: Strava application client ID
            client_secret: Strava application client secret
            code: Authorization code from OAuth flow
            
        Returns:
            Dictionary with access_token and refresh_token
        """
        token_response = self.client.exchange_code_for_token(
            client_id=client_id,
            client_secret=client_secret,
            code=code
        )
        # In stravalib v2, exchange_code_for_token returns AccessInfo (TypedDict) or tuple
        # If it's a tuple, extract the AccessInfo part
        if isinstance(token_response, tuple):
            token_response = token_response[0]
            
        self.access_token = token_response['access_token']
        self.client.access_token = self.access_token
        return {
            'access_token': token_response['access_token'],
            'refresh_token': token_response['refresh_token'],
            'expires_at': token_response['expires_at']
        }
    
    def refresh_access_token(self, client_id: int, client_secret: str, refresh_token: str) -> Dict[str, str]:
        """
        Refresh an expired access token.
        
        Args:
            client_id: Strava application client ID
            client_secret: Strava application client secret
            refresh_token: Refresh token
            
        Returns:
            Dictionary with new access_token and refresh_token
        """
        token_response = self.client.refresh_access_token(
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token
        )
        # In stravalib v2, refresh_access_token returns AccessInfo (TypedDict)
        self.access_token = token_response['access_token']
        self.client.access_token = self.access_token
        return {
            'access_token': token_response['access_token'],
            'refresh_token': token_response['refresh_token'],
            'expires_at': token_response['expires_at']
        }
    
    def get_activities(self, after: Optional[datetime] = None, before: Optional[datetime] = None, limit: int = 200) -> List[Union[SummaryActivity, DetailedActivity]]:
        """
        Fetch activities from Strava.
        
        Args:
            after: Only return activities after this date
            before: Only return activities before this date
            limit: Maximum number of activities to return
            
        Returns:
            List of Activity objects
        """
        if not self.access_token:
            raise ValueError("No access token available. Please authorize first.")
        
        activities = []
        for activity in self.client.get_activities(after=after, before=before, limit=limit):
            activities.append(activity)
        
        return activities
    
    def get_activity_details(self, activity_id: int) -> DetailedActivity:
        """
        Get detailed information for a specific activity.
        
        Args:
            activity_id: The ID of the activity
            
        Returns:
            Detailed Activity object
        """
        if not self.access_token:
            raise ValueError("No access token available. Please authorize first.")
        
        return self.client.get_activity(activity_id)
    
    def get_athlete_gear(self) -> List[Dict]:
        """
        Get the athlete's gear (shoes).
        
        Returns:
            List of gear dictionaries
        """
        if not self.access_token:
            raise ValueError("No access token available. Please authorize first.")
        
        athlete = self.client.get_athlete()
        gear = []
        
        if hasattr(athlete, 'shoes'):
            for shoe in athlete.shoes:
                gear.append({
                    'id': shoe.id,
                    'name': shoe.name,
                    'distance': float(shoe.distance) if shoe.distance else 0.0,
                    'primary': getattr(shoe, 'primary', False)
                })
        
        return gear
