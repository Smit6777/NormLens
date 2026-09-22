import os
import requests
from dotenv import load_dotenv

def main():
    print("Initiating Vector Index Rebuild...")
    
    # Load .env to get the admin key
    load_dotenv()
    admin_key = os.getenv("ADMIN_API_KEY", "admin-api-key")
    port = os.getenv("PORT", "8000")
    
    url = f"http://localhost:{port}/api/v1/rebuild-index"
    headers = {"X-API-Key": admin_key}
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("[OK] Rebuild successful!")
            print(f"Standards Indexed: {data.get('standards_indexed')}")
            print(f"Model used: {data.get('embedding_model')}")
        else:
            print(f"[ERROR] Rebuild failed with status code: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to the backend server. Is it running on port 8000?")
        
if __name__ == "__main__":
    main()
