"""Command-line interface for My Shoe Tracker."""

import argparse
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from shoe_tracker.strava_client import StravaClient
from shoe_tracker.analyzer import ActivityAnalyzer


def format_table(df, title=None):
    """Format a DataFrame as a simple text table."""
    if title:
        print(f"\n{title}")
        print("=" * len(title))
    
    if df.empty:
        print("No data available")
        return
    
    # Print to string with tabulate style
    print(df.to_string(index=False))


def main():
    """Main CLI entry point."""
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description='My Shoe Tracker - Track your running shoes with Strava',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start the web interface
  python -m shoe_tracker.cli web
  
  # Generate a summary report
  python -m shoe_tracker.cli report summary
  
  # Generate a weekly report
  python -m shoe_tracker.cli report weekly
  
  # Generate reports for the last 6 months
  python -m shoe_tracker.cli report monthly --days 180
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Web command
    web_parser = subparsers.add_parser('web', help='Start the web interface')
    web_parser.add_argument('--port', type=int, default=5000, help='Port to run the web server on')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate reports')
    report_parser.add_argument('type', choices=['summary', 'weekly', 'monthly', 'yearly', 'activities'],
                              help='Type of report to generate')
    report_parser.add_argument('--days', type=int, default=365,
                              help='Number of days to look back (default: 365)')
    report_parser.add_argument('--shoe-id', type=str, help='Filter by specific shoe ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'web':
        # Start web interface
        from shoe_tracker.app import app
        print(f"Starting web interface on http://localhost:{args.port}")
        app.run(host='0.0.0.0', port=args.port, debug=False)
        
    elif args.command == 'report':
        # Generate reports
        access_token = os.getenv('STRAVA_ACCESS_TOKEN')
        
        if not access_token:
            print("Error: STRAVA_ACCESS_TOKEN not found in environment variables.")
            print("Please set it in your .env file or export it as an environment variable.")
            print("\nTo get an access token:")
            print("1. Run the web interface: python -m shoe_tracker.cli web")
            print("2. Log in with Strava")
            print("3. Copy the access token from your session")
            sys.exit(1)
        
        try:
            # Initialize client
            print(f"Fetching activities from the last {args.days} days...")
            client = StravaClient(access_token)
            
            # Get activities
            after = datetime.now() - timedelta(days=args.days)
            activities = client.get_activities(after=after, limit=500)
            
            if not activities:
                print("No activities found in the specified time period.")
                sys.exit(0)
            
            print(f"Found {len(activities)} activities")
            
            # Get gear information
            print("Fetching gear information...")
            gear_list = client.get_athlete_gear()
            gear_info = {g['id']: g['name'] for g in gear_list}
            
            # Analyze activities
            analyzer = ActivityAnalyzer(activities)
            
            # Generate requested report
            if args.type == 'summary':
                report = analyzer.get_shoe_summary(gear_info)
                format_table(report, "Overall Shoe Summary")
                
            elif args.type == 'weekly':
                report = analyzer.get_weekly_report(gear_info)
                format_table(report, "Weekly Report")
                
            elif args.type == 'monthly':
                report = analyzer.get_monthly_report(gear_info)
                format_table(report, "Monthly Report")
                
            elif args.type == 'yearly':
                report = analyzer.get_yearly_report(gear_info)
                format_table(report, "Yearly Report")
                
            elif args.type == 'activities':
                report = analyzer.get_activities_by_shoe(args.shoe_id)
                title = f"Activities for Shoe {args.shoe_id}" if args.shoe_id else "All Activities"
                format_table(report, title)
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    main()
