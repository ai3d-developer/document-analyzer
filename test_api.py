import sys
import base64
import json
import urllib.request
import os

# Configuration
API_URL = "https://document-analyzer-n1ca.onrender.com/api/document-analyze"
API_KEY = "my-secret-token" # Replace with your actual key if you changed it!

def test_document(file_path):
    # Determine the file type based on extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower().strip('.')
    if ext not in ['pdf', 'docx', 'jpg', 'jpeg', 'png']:
        print(f"Unsupported file type: {ext}")
        return
        
    # Read and encode the file to Base64
    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            base64_string = base64.b64encode(file_bytes).decode('utf-8')
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Build the JSON Payload matching the strict rubric schema
    payload = {
        "fileName": os.path.basename(file_path),
        "fileType": "image" if ext in ['jpg', 'jpeg', 'png'] else ext,
        "fileBase64": base64_string
    }
    
    data = json.dumps(payload).encode('utf-8')

    # Build the HTTP Request
    req = urllib.request.Request(API_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("x-api-key", API_KEY)

    print(f"Sending {os.path.basename(file_path)} to {API_URL} ...")
    
    # Send Request and Print Response
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print("\n--- 🟢 API SUCCESS ---")
            print(json.dumps(result, indent=2))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"\n--- 🔴 API ERROR ({e.code}) ---")
        print(error_body)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <path_to_your_file>")
        print("Example: python test_api.py sample.pdf")
    else:
        test_document(sys.argv[1])
