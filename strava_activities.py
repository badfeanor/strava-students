import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import logging
from config import STUDENT_IDS
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import threading
import time

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AuthHandler(BaseHTTPRequestHandler):
    code = None
    
    def do_GET(self):
        """Handle GET request to the callback URL"""
        query_components = parse_qs(urlparse(self.path).query)
        
        if 'code' in query_components:
            AuthHandler.code = query_components['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Authorization successful! You can close this window.")
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Authorization failed! No code received.")

def start_auth_server(port=8000):
    """Start a local server to receive the authorization code"""
    server = HTTPServer(('localhost', port), AuthHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    return server

def get_authorization_code(client_id):
    """Get authorization code from Strava"""
    auth_url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri=http://localhost:8000&approval_prompt=force&scope=activity:read_all,read"
    
    # Start local server
    server = start_auth_server()
    
    # Open browser for authorization
    webbrowser.open(auth_url)
    
    # Wait for authorization code
    logger.info("Waiting for authorization...")
    while AuthHandler.code is None:
        time.sleep(1)
    
    # Shutdown server
    server.shutdown()
    server.server_close()
    
    return AuthHandler.code

class StravaAPI:
    def __init__(self):
        self.client_id = os.getenv('STRAVA_CLIENT_ID')
        self.client_secret = os.getenv('STRAVA_CLIENT_SECRET')
        self.refresh_token = os.getenv('STRAVA_REFRESH_TOKEN')
        self.access_token = None
        self.base_url = 'https://www.strava.com/api/v3'
        
        # Проверка наличия необходимых переменных окружения
        if not all([self.client_id, self.client_secret]):
            missing = []
            if not self.client_id:
                missing.append('STRAVA_CLIENT_ID')
            if not self.client_secret:
                missing.append('STRAVA_CLIENT_SECRET')
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        # Если нет refresh token, получаем его
        if not self.refresh_token:
            logger.info("No refresh token found. Starting authorization process...")
            auth_code = get_authorization_code(self.client_id)
            self.refresh_token = self.exchange_code_for_token(auth_code)
            logger.info("Successfully obtained refresh token")
        
    def exchange_code_for_token(self, auth_code):
        """Exchange authorization code for refresh token"""
        try:
            response = requests.post(
                'https://www.strava.com/oauth/token',
                data={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'code': auth_code,
                    'grant_type': 'authorization_code'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['refresh_token']
            else:
                logger.error(f"Failed to exchange code for token. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                raise Exception("Failed to exchange authorization code for token")
                
        except Exception as e:
            logger.error(f"Error during code exchange: {str(e)}")
            raise
        
    def get_access_token(self):
        """Exchange refresh token for a new access token"""
        try:
            logger.info("Attempting to get new access token...")
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
                logger.info("Successfully obtained new access token")
                return True
            else:
                logger.error(f"Failed to get access token. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error during token refresh: {str(e)}")
            return False

    def get_athlete_activities(self, athlete_id, per_page=10):
        """Get recent activities for a specific athlete"""
        if not self.access_token:
            if not self.get_access_token():
                raise Exception("Failed to get access token")

        headers = {'Authorization': f'Bearer {self.access_token}'}
        try:
            logger.info(f"Fetching activities for athlete {athlete_id}")
            response = requests.get(
                f'{self.base_url}/athletes/{athlete_id}/activities',
                headers=headers,
                params={'per_page': per_page}
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                # Попробуем обновить токен и повторить запрос
                logger.info("Token expired, attempting to refresh...")
                if self.get_access_token():
                    headers = {'Authorization': f'Bearer {self.access_token}'}
                    response = requests.get(
                        f'{self.base_url}/athletes/{athlete_id}/activities',
                        headers=headers,
                        params={'per_page': per_page}
                    )
                    if response.status_code == 200:
                        return response.json()
                
            logger.error(f"Failed to get activities. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            raise Exception(f"Failed to get activities: {response.status_code}")
            
        except Exception as e:
            logger.error(f"Error fetching activities for athlete {athlete_id}: {str(e)}")
            raise

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
    
    try:
        strava = StravaAPI()
        all_activities = []
        
        for student_id in STUDENT_IDS:
            try:
                activities = strava.get_athlete_activities(student_id)
                df = format_activities(activities)
                df['athlete_id'] = student_id
                all_activities.append(df)
                logger.info(f"Successfully fetched activities for athlete {student_id}")
            except Exception as e:
                logger.error(f"Error fetching activities for athlete {student_id}: {str(e)}")
        
        if all_activities:
            final_df = pd.concat(all_activities, ignore_index=True)
            output_file = os.path.join('output', 'student_activities.csv')
            final_df.to_csv(output_file, index=False)
            logger.info(f"Activities have been saved to {output_file}")
        else:
            logger.warning("No activities were fetched")
            
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 