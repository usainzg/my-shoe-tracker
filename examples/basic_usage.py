"""
Example script demonstrating how to use My Shoe Tracker programmatically.

This script shows how to:
1. Authenticate with Strava
2. Fetch activities
3. Generate various reports
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from shoe_tracker.strava_client import StravaClient
from shoe_tracker.analyzer import ActivityAnalyzer


def main():
    """Main example function."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get access token from environment
    access_token = os.getenv('STRAVA_ACCESS_TOKEN')
    
    if not access_token:
        print("Error: STRAVA_ACCESS_TOKEN not found.")
        print("Please set it in your .env file or use the web interface to authenticate.")
        return
    
    # Initialize Strava client
    print("Initializing Strava client...")
    client = StravaClient(access_token)
    
    # Fetch activities from the last 90 days
    print("\nFetching activities from the last 90 days...")
    after = datetime.now() - timedelta(days=90)
    activities = client.get_activities(after=after, limit=100)
    print(f"Found {len(activities)} activities")
    
    # Fetch gear (shoes) information
    print("\nFetching gear information...")
    gear_list = client.get_athlete_gear()
    gear_info = {g['id']: g['name'] for g in gear_list}
    
    print(f"Found {len(gear_list)} pairs of shoes:")
    for gear in gear_list:
        print(f"  - {gear['name']} (ID: {gear['id']}, Distance: {gear['distance']/1000:.2f} km)")
    
    # Create analyzer
    print("\nAnalyzing activities...")
    analyzer = ActivityAnalyzer(activities)
    
    # Generate overall shoe summary
    print("\n" + "="*80)
    print("OVERALL SHOE SUMMARY")
    print("="*80)
    shoe_summary = analyzer.get_shoe_summary(gear_info)
    print(shoe_summary.to_string(index=False))
    
    # Generate weekly report (last 4 weeks)
    print("\n" + "="*80)
    print("WEEKLY REPORT (Last 4 weeks)")
    print("="*80)
    weekly_report = analyzer.get_weekly_report(gear_info).head(4)
    if not weekly_report.empty:
        print(weekly_report.to_string(index=False))
    else:
        print("No weekly data available")
    
    # Generate monthly report
    print("\n" + "="*80)
    print("MONTHLY REPORT")
    print("="*80)
    monthly_report = analyzer.get_monthly_report(gear_info)
    if not monthly_report.empty:
        print(monthly_report.to_string(index=False))
    else:
        print("No monthly data available")
    
    # Generate yearly report
    print("\n" + "="*80)
    print("YEARLY REPORT")
    print("="*80)
    yearly_report = analyzer.get_yearly_report(gear_info)
    if not yearly_report.empty:
        print(yearly_report.to_string(index=False))
    else:
        print("No yearly data available")
    
    # Show activities for a specific shoe (if available)
    if not shoe_summary.empty and len(shoe_summary) > 0:
        first_gear_id = shoe_summary.iloc[0]['gear_id']
        shoe_name = shoe_summary.iloc[0]['shoe_name']
        
        print("\n" + "="*80)
        print(f"RECENT ACTIVITIES FOR: {shoe_name}")
        print("="*80)
        shoe_activities = analyzer.get_activities_by_shoe(first_gear_id).head(5)
        if not shoe_activities.empty:
            print(shoe_activities.to_string(index=False))
        else:
            print("No activities found for this shoe")
    
    print("\n" + "="*80)
    print("Analysis complete!")
    print("="*80)


if __name__ == '__main__':
    main()
