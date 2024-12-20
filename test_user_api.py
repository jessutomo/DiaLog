import requests
import json  # Optional, for pretty-printing the response if needed

url = "http://127.0.0.1:5000/register"

data = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "password": "securepassword",
    "confirm_password": "securepassword",
    "gender": "Male",
    "birthdate": "1990-01-01",
    "country_of_residence": "USA",
    "emergency_contact": "+1234567890",
    "weight": 70,
    "height": 175,
    "consent": True
}

# Send the POST request
response = requests.post(url, json=data)

# Print the response
print(f"Status Code: {response.status_code}")
print("Response:", json.dumps(response.json(), indent=2))

