
import base64
import requests

API_URL = "http://localhost:8000/"  # Testing root POST
HEADERS = {"x-api-key": "my-secret-token"}

# Small dummy base64 to test if it accepts it
dummy_content = base64.b64encode(b"This is a test document content.").decode('utf-8')

payload = {
    "fileName": "test.txt",
    "fileType": "text",
    "fileBase64": dummy_content
}

print(f"Testing POST to {API_URL}...")
try:
    response = requests.post(API_URL, json=payload, headers=HEADERS)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
