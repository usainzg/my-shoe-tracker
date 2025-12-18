"""Flask web application for My Shoe Tracker."""

import os
import secrets
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
from shoe_tracker.strava_client import StravaClient
from shoe_tracker.analyzer import ActivityAnalyzer

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get secret key from environment or generate a random one for development
secret_key = os.getenv('FLASK_SECRET_KEY')
if not secret_key:
    # Generate a random secret key for development
    secret_key = secrets.token_hex(32)
    print("WARNING: Using a randomly generated secret key. Set FLASK_SECRET_KEY in .env for production.")

app.secret_key = secret_key

# Strava OAuth settings
STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5000/auth/callback'


@app.route('/')
def index():
    """Home page."""
    access_token = session.get('access_token')
    
    if not access_token:
        # Not authenticated
        return render_template('index.html', authenticated=False)
    
    try:
        # Fetch activities
        client = StravaClient(access_token)
        
        # Get activities from the last year
        after = datetime.now() - timedelta(days=365)
        activities = client.get_activities(after=after, limit=200)
        
        # Get gear information
        gear_list = client.get_athlete_gear()
        gear_info = {g['id']: g['name'] for g in gear_list}
        
        # Analyze activities
        analyzer = ActivityAnalyzer(activities)
        
        # Get different report types
        shoe_summary = analyzer.get_shoe_summary(gear_info)
        weekly_report = analyzer.get_weekly_report(gear_info).head(10)  # Last 10 weeks
        monthly_report = analyzer.get_monthly_report(gear_info).head(6)  # Last 6 months
        yearly_report = analyzer.get_yearly_report(gear_info)
        
        return render_template('index.html',
                             authenticated=True,
                             shoe_summary=shoe_summary.to_html(classes='table table-striped', index=False, escape=True) if not shoe_summary.empty else None,
                             weekly_report=weekly_report.to_html(classes='table table-striped', index=False, escape=True) if not weekly_report.empty else None,
                             monthly_report=monthly_report.to_html(classes='table table-striped', index=False, escape=True) if not monthly_report.empty else None,
                             yearly_report=yearly_report.to_html(classes='table table-striped', index=False, escape=True) if not yearly_report.empty else None,
                             activity_count=len(activities),
                             gear_count=len(gear_list))
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'error')
        return render_template('index.html', authenticated=True, error=str(e))


@app.route('/auth/login')
def login():
    """Redirect to Strava authorization page."""
    if not STRAVA_CLIENT_ID:
        flash('Strava Client ID not configured. Please set STRAVA_CLIENT_ID in .env file.', 'error')
        return redirect(url_for('index'))
    
    auth_url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={STRAVA_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=read,activity:read_all"
    )
    return redirect(auth_url)


@app.route('/auth/callback')
def auth_callback():
    """Handle OAuth callback from Strava."""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        flash(f'Authorization error: {error}', 'error')
        return redirect(url_for('index'))
    
    if not code:
        flash('No authorization code received', 'error')
        return redirect(url_for('index'))
    
    try:
        client = StravaClient()
        token_data = client.authorize(
            client_id=int(STRAVA_CLIENT_ID),
            client_secret=STRAVA_CLIENT_SECRET,
            code=code
        )
        
        # Store tokens in session
        session['access_token'] = token_data['access_token']
        session['refresh_token'] = token_data['refresh_token']
        session['expires_at'] = token_data['expires_at']
        
        flash('Successfully authenticated with Strava!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Authentication error: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/auth/logout')
def logout():
    """Log out the user."""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))


@app.route('/reports/weekly')
def weekly_report():
    """Show detailed weekly report."""
    access_token = session.get('access_token')
    
    if not access_token:
        flash('Please log in first', 'error')
        return redirect(url_for('index'))
    
    try:
        client = StravaClient(access_token)
        after = datetime.now() - timedelta(days=365)
        activities = client.get_activities(after=after, limit=200)
        
        gear_list = client.get_athlete_gear()
        gear_info = {g['id']: g['name'] for g in gear_list}
        
        analyzer = ActivityAnalyzer(activities)
        report = analyzer.get_weekly_report(gear_info)
        
        return render_template('report.html',
                             title='Weekly Report',
                             report=report.to_html(classes='table table-striped', index=False, escape=True) if not report.empty else None)
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/reports/monthly')
def monthly_report():
    """Show detailed monthly report."""
    access_token = session.get('access_token')
    
    if not access_token:
        flash('Please log in first', 'error')
        return redirect(url_for('index'))
    
    try:
        client = StravaClient(access_token)
        after = datetime.now() - timedelta(days=365)
        activities = client.get_activities(after=after, limit=200)
        
        gear_list = client.get_athlete_gear()
        gear_info = {g['id']: g['name'] for g in gear_list}
        
        analyzer = ActivityAnalyzer(activities)
        report = analyzer.get_monthly_report(gear_info)
        
        return render_template('report.html',
                             title='Monthly Report',
                             report=report.to_html(classes='table table-striped', index=False, escape=True) if not report.empty else None)
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/reports/yearly')
def yearly_report():
    """Show detailed yearly report."""
    access_token = session.get('access_token')
    
    if not access_token:
        flash('Please log in first', 'error')
        return redirect(url_for('index'))
    
    try:
        client = StravaClient(access_token)
        after = datetime.now() - timedelta(days=365*3)  # Last 3 years
        activities = client.get_activities(after=after, limit=500)
        
        gear_list = client.get_athlete_gear()
        gear_info = {g['id']: g['name'] for g in gear_list}
        
        analyzer = ActivityAnalyzer(activities)
        report = analyzer.get_yearly_report(gear_info)
        
        return render_template('report.html',
                             title='Yearly Report',
                             report=report.to_html(classes='table table-striped', index=False, escape=True) if not report.empty else None)
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'error')
        return redirect(url_for('index'))


def main():
    """Main entry point for the application."""
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


if __name__ == '__main__':
    main()
