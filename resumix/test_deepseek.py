import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_deepseek_connection():
    """Test DeepSeek API connection with proper error handling"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    api_url = os.getenv("DEEPSEEK_API_URL")
    
    if not api_key:
        print("❌ Error: DEEPSEEK_API_KEY not found in .env file")
        return False
        
    if not api_url:
        print("❌ Error: DEEPSEEK_API_URL not found in .env file")
        return False

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "Just say 'OK'"}],
        "max_tokens": 5,
        "temperature": 0
    }

    try:
        print("🔍 Testing DeepSeek API connection...")
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=10
        )
        
        # Check HTTP status
        if response.status_code == 200:
            print("✅ DeepSeek API connection successful!")
            print(f"Response: {response.json()}")
            return True
        else:
            error_msg = response.json().get("error", {}).get("message", "Unknown error")
            print(f"❌ API Error {response.status_code}: {error_msg}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {str(e)}")
        print("Possible solutions:")
        print("1. Check your internet connection")
        print("2. Verify the API URL is correct")
        print("3. Ensure your API key is valid")
        return False

if __name__ == "__main__":
    test_deepseek_connection()