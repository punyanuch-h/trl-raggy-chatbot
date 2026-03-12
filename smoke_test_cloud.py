import requests
import json

URL = "https://raggy-bot-api-1086580567841.us-east1.run.app/raggy/trl"
# Token signed with "raggy-secret-2026"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiVEVTVC0wMDEiLCJyb2xlIjoiYWRtaW4ifQ.w1QcaWugOMGE-nNyGyyY-WZ1sH4hzOVBDudFfW-_eg0"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}
payload = {
    "query": "What are TRL levels 1 to 9?"
}

try:
    response = requests.post(URL, headers=headers, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
