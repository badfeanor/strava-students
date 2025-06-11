# Strava Students Activities Analysis

This project fetches the last 10 activities for a list of students from Strava API and saves them to a CSV file.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a Strava API application:
   - Go to https://www.strava.com/settings/api
   - Create a new application
   - Note down your Client ID and Client Secret

3. Create a `.env` file in the project root with the following content:
```
STRAVA_CLIENT_ID=your_client_id_here
STRAVA_CLIENT_SECRET=your_client_secret_here
STRAVA_REFRESH_TOKEN=your_refresh_token_here
```

4. To get a refresh token:
   - Visit: https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=read,activity:read
   - Authorize the application
   - Copy the code from the redirect URL
   - Exchange the code for tokens using:
     ```
     curl -X POST https://www.strava.com/oauth/token \
     -F client_id=YOUR_CLIENT_ID \
     -F client_secret=YOUR_CLIENT_SECRET \
     -F code=AUTHORIZATION_CODE \
     -F grant_type=authorization_code
     ```
   - Use the refresh_token from the response in your .env file

5. Edit the `student_ids` list in `strava_activities.py` to include the Strava athlete IDs of your students.

## Usage

Run the script:
```bash
python strava_activities.py
```

The script will:
1. Authenticate with Strava API
2. Fetch the last 10 activities for each student
3. Save the results to `student_activities.csv`

## Output

The CSV file will contain the following information for each activity:
- Activity name
- Activity type
- Distance (km)
- Moving time (minutes)
- Elapsed time (minutes)
- Total elevation gain (meters)
- Start date
- Average speed (km/h)
- Max speed (km/h)
- Athlete ID 