import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class StravaAPI:
    def __init__(self):
        self.client_id = os.getenv('STRAVA_CLIENT_ID')
        self.client_secret = os.getenv('STRAVA_CLIENT_SECRET')
        self.refresh_token = os.getenv('STRAVA_REFRESH_TOKEN')
        self.access_token = None
        self.base_url = 'https://www.strava.com/api/v3'
        
    def get_access_token(self):
        """Exchange refresh token for a new access token"""
        response = requests.post(
            'https://www.strava.com/api/v3/oauth/token',
            data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token'
            }
        )
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            # Обновляем refresh_token, так как он может измениться
            self.refresh_token = data['refresh_token']
            return True
        return False

    def get_athlete_activities(self, athlete_id, per_page=10):
        """Get recent activities for a specific athlete"""
        if not self.access_token:
            if not self.get_access_token():
                raise Exception("Failed to get access token")

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(
            f'{self.base_url}/athletes/{athlete_id}/activities',
            headers=headers,
            params={'per_page': per_page}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get activities: {response.status_code}")

def format_activities(activities):
    """Format activities into a pandas DataFrame"""
    formatted_activities = []
    for activity in activities:
        formatted_activities.append({
            'name': activity['name'],
            'type': activity['type'],
            'distance': round(activity['distance'] / 1000, 2),  # Convert to km
            'moving_time': round(activity['moving_time'] / 60, 2),  # Convert to minutes
            'elapsed_time': round(activity['elapsed_time'] / 60, 2),  # Convert to minutes
            'total_elevation_gain': round(activity['total_elevation_gain'], 2),
            'start_date': datetime.fromisoformat(activity['start_date'].replace('Z', '+00:00')),
            'average_speed': round(activity['average_speed'] * 3.6, 2),  # Convert to km/h
            'max_speed': round(activity['max_speed'] * 3.6, 2),  # Convert to km/h
        })
    return pd.DataFrame(formatted_activities)

def main():
    # Создаем директорию output, если она не существует
    os.makedirs('output', exist_ok=True)
    
    # List of student athlete IDs
    student_ids = [
        # Add student IDs here
    ]
    
    strava = StravaAPI()
    all_activities = []
    
    for student_id in student_ids:
        try:
            activities = strava.get_athlete_activities(student_id)
            df = format_activities(activities)
            df['athlete_id'] = student_id
            all_activities.append(df)
        except Exception as e:
            print(f"Error fetching activities for athlete {student_id}: {str(e)}")
    
    if all_activities:
        final_df = pd.concat(all_activities, ignore_index=True)
        output_file = os.path.join('output', 'student_activities.csv')
        final_df.to_csv(output_file, index=False)
        print(f"Activities have been saved to {output_file}")
    else:
        print("No activities were fetched")

if __name__ == "__main__":
    main() 