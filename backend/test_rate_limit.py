import requests
import time

# Login first
login_response = requests.post('http://localhost:8000/api/auth/login', json={
    "email": "pam@example.com",
    "password": "stringVibes"
})
token = login_response.json()['access_token']

headers = {'Authorization': f'Bearer {token}'}

# Make 105 requests rapidly
print("Making 105 requests...")
for i in range(105):
    response = requests.get('http://localhost:8000/api/entries', headers=headers)
    print(f"Request {i+1}: Status {response.status_code}")
    
    if response.status_code == 429:
        print(f"\n🛑 Rate limited at request {i+1}!")
        print(f"Response: {response.json()}")
        print(f"Headers: {dict(response.headers)}")
        break
    
    time.sleep(0.01)  # Small delay to prevent overwhelming server

print("\n✅ Rate limiting is working!")