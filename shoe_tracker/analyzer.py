"""Data analyzer for processing Strava activities and generating reports."""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
from collections import defaultdict
import pandas as pd
from stravalib.strava_model import SummaryActivity, DetailedActivity


class ActivityAnalyzer:
    """Analyzes Strava activities and generates shoe-based reports."""
    
    def __init__(self, activities: List[Union[SummaryActivity, DetailedActivity]]):
        """
        Initialize the analyzer with activities.
        
        Args:
            activities: List of Strava Activity objects
        """
        self.activities = activities
        self.df = self._activities_to_dataframe()
    
    def _activities_to_dataframe(self) -> pd.DataFrame:
        """Convert activities to a pandas DataFrame for easier analysis."""
        data = []
        
        for activity in self.activities:
            # Extract relevant fields
            # In stravalib v2, moving_time and elapsed_time are int (seconds) instead of timedelta
            record = {
                'id': activity.id,
                'name': activity.name,
                'type': str(activity.type) if activity.type else 'Unknown',
                'date': activity.start_date_local,
                'distance_km': float(activity.distance) / 1000 if activity.distance else 0.0,
                'moving_time_hours': float(activity.moving_time) / 3600 if activity.moving_time else 0.0,
                'elapsed_time_hours': float(activity.elapsed_time) / 3600 if activity.elapsed_time else 0.0,
                'elevation_gain_m': float(activity.total_elevation_gain) if activity.total_elevation_gain else 0.0,
                'gear_id': activity.gear_id if hasattr(activity, 'gear_id') and activity.gear_id else None,
            }
            data.append(record)
        
        df = pd.DataFrame(data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df['year'] = df['date'].dt.year
            df['month'] = df['date'].dt.month
            df['week'] = df['date'].dt.isocalendar().week
            df['year_week'] = df['date'].dt.strftime('%Y-W%U')
            df['year_month'] = df['date'].dt.strftime('%Y-%m')
        
        return df
    
    def get_shoe_summary(self, gear_info: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        Get overall summary statistics by shoe.
        
        Args:
            gear_info: Dictionary mapping gear_id to gear name
            
        Returns:
            DataFrame with shoe summaries
        """
        if self.df.empty:
            return pd.DataFrame()
        
        # Group by gear_id
        summary = self.df.groupby('gear_id').agg({
            'distance_km': 'sum',
            'moving_time_hours': 'sum',
            'elapsed_time_hours': 'sum',
            'elevation_gain_m': 'sum',
            'id': 'count'
        }).reset_index()
        
        summary.columns = ['gear_id', 'total_distance_km', 'total_moving_time_hours', 
                          'total_elapsed_time_hours', 'total_elevation_gain_m', 'activity_count']
        
        # Add gear names if provided
        if gear_info:
            summary['shoe_name'] = summary['gear_id'].map(gear_info)
            summary['shoe_name'] = summary['shoe_name'].fillna('Unknown Shoe')
        else:
            summary['shoe_name'] = summary['gear_id'].apply(
                lambda x: f'Shoe {x}' if x else 'No Shoe'
            )
        
        # Round values for readability
        summary['total_distance_km'] = summary['total_distance_km'].round(2)
        summary['total_moving_time_hours'] = summary['total_moving_time_hours'].round(2)
        summary['total_elapsed_time_hours'] = summary['total_elapsed_time_hours'].round(2)
        summary['total_elevation_gain_m'] = summary['total_elevation_gain_m'].round(2)
        
        return summary[['shoe_name', 'gear_id', 'total_distance_km', 'total_moving_time_hours', 
                       'total_elevation_gain_m', 'activity_count']]
    
    def get_weekly_report(self, gear_info: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        Get weekly statistics by shoe.
        
        Args:
            gear_info: Dictionary mapping gear_id to gear name
            
        Returns:
            DataFrame with weekly shoe statistics
        """
        if self.df.empty:
            return pd.DataFrame()
        
        weekly = self.df.groupby(['year_week', 'gear_id']).agg({
            'distance_km': 'sum',
            'moving_time_hours': 'sum',
            'elevation_gain_m': 'sum',
            'id': 'count'
        }).reset_index()
        
        weekly.columns = ['week', 'gear_id', 'distance_km', 'moving_time_hours', 
                         'elevation_gain_m', 'activity_count']
        
        # Add gear names if provided
        if gear_info:
            weekly['shoe_name'] = weekly['gear_id'].map(gear_info)
            weekly['shoe_name'] = weekly['shoe_name'].fillna('Unknown Shoe')
        else:
            weekly['shoe_name'] = weekly['gear_id'].apply(
                lambda x: f'Shoe {x}' if x else 'No Shoe'
            )
        
        # Round values
        weekly['distance_km'] = weekly['distance_km'].round(2)
        weekly['moving_time_hours'] = weekly['moving_time_hours'].round(2)
        weekly['elevation_gain_m'] = weekly['elevation_gain_m'].round(2)
        
        return weekly[['week', 'shoe_name', 'gear_id', 'distance_km', 
                      'moving_time_hours', 'elevation_gain_m', 'activity_count']].sort_values('week', ascending=False)
    
    def get_monthly_report(self, gear_info: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        Get monthly statistics by shoe.
        
        Args:
            gear_info: Dictionary mapping gear_id to gear name
            
        Returns:
            DataFrame with monthly shoe statistics
        """
        if self.df.empty:
            return pd.DataFrame()
        
        monthly = self.df.groupby(['year_month', 'gear_id']).agg({
            'distance_km': 'sum',
            'moving_time_hours': 'sum',
            'elevation_gain_m': 'sum',
            'id': 'count'
        }).reset_index()
        
        monthly.columns = ['month', 'gear_id', 'distance_km', 'moving_time_hours', 
                          'elevation_gain_m', 'activity_count']
        
        # Add gear names if provided
        if gear_info:
            monthly['shoe_name'] = monthly['gear_id'].map(gear_info)
            monthly['shoe_name'] = monthly['shoe_name'].fillna('Unknown Shoe')
        else:
            monthly['shoe_name'] = monthly['gear_id'].apply(
                lambda x: f'Shoe {x}' if x else 'No Shoe'
            )
        
        # Round values
        monthly['distance_km'] = monthly['distance_km'].round(2)
        monthly['moving_time_hours'] = monthly['moving_time_hours'].round(2)
        monthly['elevation_gain_m'] = monthly['elevation_gain_m'].round(2)
        
        return monthly[['month', 'shoe_name', 'gear_id', 'distance_km', 
                       'moving_time_hours', 'elevation_gain_m', 'activity_count']].sort_values('month', ascending=False)
    
    def get_yearly_report(self, gear_info: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        Get yearly statistics by shoe.
        
        Args:
            gear_info: Dictionary mapping gear_id to gear name
            
        Returns:
            DataFrame with yearly shoe statistics
        """
        if self.df.empty:
            return pd.DataFrame()
        
        yearly = self.df.groupby(['year', 'gear_id']).agg({
            'distance_km': 'sum',
            'moving_time_hours': 'sum',
            'elevation_gain_m': 'sum',
            'id': 'count'
        }).reset_index()
        
        yearly.columns = ['year', 'gear_id', 'distance_km', 'moving_time_hours', 
                         'elevation_gain_m', 'activity_count']
        
        # Add gear names if provided
        if gear_info:
            yearly['shoe_name'] = yearly['gear_id'].map(gear_info)
            yearly['shoe_name'] = yearly['shoe_name'].fillna('Unknown Shoe')
        else:
            yearly['shoe_name'] = yearly['gear_id'].apply(
                lambda x: f'Shoe {x}' if x else 'No Shoe'
            )
        
        # Round values
        yearly['distance_km'] = yearly['distance_km'].round(2)
        yearly['moving_time_hours'] = yearly['moving_time_hours'].round(2)
        yearly['elevation_gain_m'] = yearly['elevation_gain_m'].round(2)
        
        return yearly[['year', 'shoe_name', 'gear_id', 'distance_km', 
                      'moving_time_hours', 'elevation_gain_m', 'activity_count']].sort_values('year', ascending=False)
    
    def get_activities_by_shoe(self, gear_id: Optional[str] = None) -> pd.DataFrame:
        """
        Get detailed activity list for a specific shoe or all shoes.
        
        Args:
            gear_id: Filter by specific gear_id, or None for all
            
        Returns:
            DataFrame with activity details
        """
        if self.df.empty:
            return pd.DataFrame()
        
        result = self.df.copy()
        if gear_id:
            result = result[result['gear_id'] == gear_id]
        
        return result[['date', 'name', 'type', 'distance_km', 'moving_time_hours', 
                      'elevation_gain_m', 'gear_id']].sort_values('date', ascending=False)
