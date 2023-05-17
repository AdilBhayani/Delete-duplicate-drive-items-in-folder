from googleapiclient.discovery import build
from google.auth import exceptions
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import json

# Set the OAuth2 scopes required for accessing Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

# Set the path to the credentials JSON file
CREDENTIALS_FILE = 'credentials.json'

FOLDER_ID = input(
    "Enter the ID of the folder you want to search for duplicate files: ")

# Load the OAuth2 credentials from the credentials file
creds = None
if os.path.exists(CREDENTIALS_FILE):
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=56146)
    except exceptions.DefaultCredentialsError as e:
        print(f"Error loading credentials: {e}")
        exit(1)
else:
    print(f"Credentials file not found: {CREDENTIALS_FILE}")
    exit(1)

# Build the Google Drive API client
drive_service = build('drive', 'v3', credentials=creds)

page_token = None
file_dict = {}
duplicate_files = []

while True:
    results = drive_service.files().list(
        q=f"parents in '{FOLDER_ID}' and trashed = false",
        fields="nextPageToken, files(name,id)",
        pageSize=1000,
        pageToken=page_token
    ).execute()

    files = results.get('files', [])
    for file in files:
        if file['name'] in file_dict:
            duplicate_files.append({'id': file['id'], 'name': file['name']})
        else:
            file_dict[file['name']] = file['name']

    page_token = results.get('nextPageToken')
    if not page_token:
        break

print("Found the following duplicates:")
print(json.dumps(duplicate_files, sort_keys=True, indent=4))

shouldDelete = input("Enter 'Y' or 'y' to delete or anything else to not delete: ")

if (shouldDelete.lower() == 'y'):
    # Delete duplicate files
    for file_data in duplicate_files:
        file_id = file_data['id']
        drive_service.files().delete(fileId=file_id).execute()
    print(f"Deleted {len(duplicate_files)} duplicate photos.")
else:
    print('No deletions performed')

