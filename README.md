# My Shoe Tracker 👟

A web application that integrates with Strava's API to track and analyze your running shoes. Get detailed insights on distance, time, and elevation gain for each pair of shoes with weekly, monthly, and yearly reports.

## Features

- 🔐 **Strava OAuth Integration** - Secure authentication with Strava
- 📊 **Activity Analysis** - Automatic analysis of all your Strava activities
- 👟 **Shoe Tracking** - Track metrics for each pair of running shoes
- 📅 **Multiple Report Types**:
  - Weekly reports - Last 52 weeks of activity
  - Monthly reports - Last 12 months of activity
  - Yearly reports - Multi-year statistics
- 📈 **Metrics Tracked**:
  - Total distance (km)
  - Moving time (hours)
  - Elevation gain (meters)
  - Activity count per shoe

## Prerequisites

- Python 3.9 or higher
- A Strava account
- Strava API credentials (Client ID and Client Secret)

## Getting Your Strava API Credentials

1. Go to [https://www.strava.com/settings/api](https://www.strava.com/settings/api)
2. Create a new application (if you haven't already)
3. Note down your **Client ID** and **Client Secret**
4. Set the Authorization Callback Domain to `localhost` (for local development)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/usainzg/my-shoe-tracker.git
cd my-shoe-tracker
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:
```bash
cp .env.example .env
```

5. Edit `.env` and add your Strava credentials:
```
STRAVA_CLIENT_ID=your_client_id_here
STRAVA_CLIENT_SECRET=your_client_secret_here
FLASK_SECRET_KEY=your_random_secret_key_here
FLASK_PORT=5000
```

## Usage

### Running the Web Application

1. Start the Flask application:
```bash
python -m shoe_tracker.cli web
```

Or directly:
```bash
python -m shoe_tracker.app
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Click "Connect with Strava" to authenticate

4. Once authenticated, you'll see your dashboard with:
   - Overall shoe summary
   - Recent weekly reports
   - Recent monthly reports
   - Yearly statistics

### Using the Command-Line Interface (CLI)

The CLI provides a convenient way to generate reports without using the web interface.

**View available commands:**
```bash
python -m shoe_tracker.cli --help
```

**Start the web server:**
```bash
python -m shoe_tracker.cli web
python -m shoe_tracker.cli web --port 8080  # Custom port
```

**Generate reports** (requires STRAVA_ACCESS_TOKEN in .env):
```bash
# Overall shoe summary
python -m shoe_tracker.cli report summary

# Weekly report
python -m shoe_tracker.cli report weekly

# Monthly report
python -m shoe_tracker.cli report monthly

# Yearly report
python -m shoe_tracker.cli report yearly

# All activities
python -m shoe_tracker.cli report activities

# Filter by time period (last 180 days)
python -m shoe_tracker.cli report monthly --days 180

# Filter by specific shoe
python -m shoe_tracker.cli report activities --shoe-id g12345678
```

### Programmatic Usage

See the `examples/basic_usage.py` file for a complete example of how to use the library programmatically:

```bash
python examples/basic_usage.py
```

Example code:
```python
from shoe_tracker.strava_client import StravaClient
from shoe_tracker.analyzer import ActivityAnalyzer
from datetime import datetime, timedelta

# Initialize client
client = StravaClient(access_token="your_token")

# Fetch activities
after = datetime.now() - timedelta(days=90)
activities = client.get_activities(after=after)

# Get gear info
gear = client.get_athlete_gear()
gear_info = {g['id']: g['name'] for g in gear}

# Analyze
analyzer = ActivityAnalyzer(activities)
summary = analyzer.get_shoe_summary(gear_info)
weekly = analyzer.get_weekly_report(gear_info)
```

### Navigating the Application

- **Home Dashboard**: Overview of all your tracked shoes and recent activity summaries
- **Weekly Report**: Detailed week-by-week breakdown by shoe
- **Monthly Report**: Monthly statistics for each shoe
- **Yearly Report**: Annual totals and comparisons

## Project Structure

```
my-shoe-tracker/
├── shoe_tracker/
│   ├── __init__.py          # Package initialization
│   ├── app.py               # Flask web application
│   ├── strava_client.py     # Strava API client
│   ├── analyzer.py          # Activity analysis and reporting
│   └── templates/           # HTML templates
│       ├── base.html        # Base template
│       ├── index.html       # Home page
│       └── report.html      # Report pages
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Project configuration
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## How It Works

1. **Authentication**: The app uses Strava's OAuth2 flow to authenticate users
2. **Data Fetching**: Once authenticated, it fetches your activities using the Strava API
3. **Analysis**: Activities are analyzed and grouped by the shoes used
4. **Reporting**: Statistics are calculated and displayed in various time periods

## API Documentation

### StravaClient

The `StravaClient` class handles all interactions with the Strava API:

```python
from shoe_tracker.strava_client import StravaClient

client = StravaClient(access_token="your_token")
activities = client.get_activities(after=datetime(2024, 1, 1))
gear = client.get_athlete_gear()
```

### ActivityAnalyzer

The `ActivityAnalyzer` class processes activities and generates reports:

```python
from shoe_tracker.analyzer import ActivityAnalyzer

analyzer = ActivityAnalyzer(activities)
shoe_summary = analyzer.get_shoe_summary(gear_info)
weekly = analyzer.get_weekly_report(gear_info)
monthly = analyzer.get_monthly_report(gear_info)
yearly = analyzer.get_yearly_report(gear_info)
```

## Troubleshooting

### "No access token available"
- Make sure you've completed the OAuth flow by clicking "Connect with Strava"
- Check that your `.env` file has the correct `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET`

### "No activities found"
- Ensure you have activities in Strava with shoes assigned
- The app fetches activities from the last year by default
- Make sure your Strava privacy settings allow API access to your activities

### OAuth Redirect Issues
- Ensure your Strava API application has `localhost` set as the Authorization Callback Domain
- The redirect URI must be `http://localhost:5000/auth/callback`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with [stravalib](https://github.com/stravalib/stravalib) - Python client for Strava API
- Uses [Flask](https://flask.palletsprojects.com/) for the web interface
- Data analysis powered by [pandas](https://pandas.pydata.org/)

## Support

If you encounter any issues or have questions, please open an issue on GitHub.