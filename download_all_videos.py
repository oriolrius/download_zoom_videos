#!/usr/bin/env python3
import os
import sys
import logging
import base64
from datetime import datetime
import pytz
import structlog
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv()

level = os.environ.get("LOG_LEVEL", "DEBUG").upper()
LOG_LEVEL = getattr(logging, level)

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(LOG_LEVEL))
logger = structlog.get_logger()
account_id = os.getenv('ACCOUNT_ID', '')

client_id = os.getenv('CLIENT_ID', '')
client_secret = os.getenv('CLIENT_SECRET', '')

def generate_filename(ts, recording_tz):
    """
    Generate a filename based on the provided timestamp and timezone, 
    converting it to 'Europe/Madrid' timezone.

    Parameters:
    - ts (str): A timestamp string in the format "2023-09-05T05:00:32Z".
    - recording_tz (str): A string representing the timezone in which the 
        recording took place, e.g., "GMT+08:00".

    Returns:
    - str: A filename string in the format "2023-09-05T13-00-32+0800", 
        with the timestamp converted to 'Europe/Madrid' timezone.
    """
    logger.debug(f'Timestamp: {ts} - Timezone: {recording_tz}')
    ts_dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")

    # Assuming recording_tz is a string like "GMT+08:00 or GMT+8:00"
    offset_str = recording_tz.split(":")[0][-2:].lstrip('+').lstrip('-')
    sign = recording_tz[3]
    tz_name = f'Etc/GMT{sign}{offset_str}'
    logger.debug(f'TZ Name: {tz_name}')

    tz = pytz.timezone(tz_name)
    ts_dt_tz = ts_dt.replace(tzinfo=pytz.utc).astimezone(tz)
    local_tz = pytz.timezone('Europe/Madrid')
    local_ts_dt_tz = ts_dt_tz.astimezone(local_tz)
    filename = local_ts_dt_tz.strftime('%Y-%m-%dT%H-%M-%S%z')  # example: 2023-09-05T13-00-32+0800
    logger.debug(f'Filename: {filename}')

    return filename


# Combine the client_id and client_secret with a colon
combined = f"{client_id}:{client_secret}"
# Encode it to base64
basic_auth = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
# Now you can use this in your header
authorization_header = f"Basic {basic_auth}"

# getting access token
url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={account_id}"
payload = {}
headers = {
  'Authorization': authorization_header
}

response = requests.request("POST", url, headers=headers, data=payload, timeout=10)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON data to a Python dictionary
    json_data = response.json()
    # Extract the access token
    access_token = json_data.get('access_token')
    logger.debug(f'Access Token: {access_token}')
else:
    logger.error(f'Failed to get data: {response.status_code}')
    sys.exit(1)

# getting all recordings from the last year
# Get the current date
current_date = datetime.now().date()
# Subtract one year
one_year_earlier = datetime(current_date.year - 1, current_date.month, current_date.day).date()
# Format the date to a string in YYYY-MM-DD format
formatted_date = one_year_earlier.strftime('%Y-%m-%d')
url = f"https://api.zoom.us/v2/users/me/recordings?from={formatted_date}"
headers = {
  'Authorization': f'Bearer {access_token}'
}
payload = {}
response = requests.request("GET", url, headers=headers, data=payload, timeout=10)
# Empty list to store MP4 download URLs
mp4_download_urls = []

if response.status_code != 200:
    logger.error(f'Failed to get data: {response.status_code}')
    sys.exit(2)

logger.debug(f'Recordings list downloaded: {response.status_code}')
# Parse the JSON data to a Python dictionary
json_data = response.json()
logger.debug(f'JSON data: {json_data}')

# Iterate through each meeting
meetings = [] # list of meetings to delete
for meeting in json_data.get("meetings", []):
    # Iterate through each recording file
    # logger.debug(f'Meeting: {meeting}')
    recording_tz = meeting.get("timezone") # "GMT+08:00"
    for recording_file in meeting.get("recording_files", []):
        # logger.debug(f'Recording file: {recording_file}')
        # Check if the file type is MP4
        if recording_file.get("file_type") == "MP4":
            # logger.debug(f'Adding MP4 file: {recording_file.get("download_url")}')
            # Append the download URL and when the meeting started
            mp4_download_urls.append({
                'url': recording_file.get("download_url"),
                'start': recording_file.get("recording_start"),
                })
            # Append the meeting ID to the list
            if meeting.get("id") not in meetings:
                meetings.append(meeting.get("id"))
logger.debug(f'MP4 download URLs: {mp4_download_urls}')
logger.debug(f'Meetings to delete: {meetings}')

# Download all MP4 files
for mp4_download_url in mp4_download_urls:
    # Get the file name from the URL
    ts = mp4_download_url.get("start") # ex. ts = "2023-09-05T05:00:32Z"
    filename = generate_filename(ts, recording_tz)
    file_name = f'{filename}.mp4'
    logger.info(f'Downloading {file_name}...')

    # Download the MP4 file
    url = mp4_download_url.get("url")
    logger.debug(f'URL: {url}')
    response = response = requests.request("GET", url, headers=headers, data=payload, timeout=10)

    # Check if the request was successful
    if response.status_code != 200:
        logger.error(f'Failed to download {file_name}: {response.status_code}')
        sys.exit(3)
    # Save the file
    with open(file_name, "wb") as f:
        f.write(response.content)
    logger.info(f'{file_name} downloaded successfully.')

# Remove meetings
for meeting_id in meetings:
    # https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/#operation/recordingDelete
    url = f"https://api.zoom.us/v2/meetings/{meeting_id}/recordings"
    logger.debug(f'Deleting meeting files. ID {meeting_id}...')
    logger.debug(f'URL: {url}')
    response = requests.request("DELETE", url, headers=headers, data=payload, timeout=10)
    if response.status_code != 204 and response.status_code != 200:
        logger.error(f'Failed to delete the file: {response.status_code}')
        sys.exit(4)
    logger.info(f'Meeting ID {meeting_id} files deleted successfully.')
