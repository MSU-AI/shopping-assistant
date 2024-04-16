import requests

# The URL of the API endpoint
url = "https://api.easymc.io/v1/token/redeem"

# The Alt-Token you want to redeem
token = "wyYR0tbIUPF8sR4BaKIY"

# The JSON body of the request
data = {
    "token": token
}

# Perform a POST request to the API endpoint
response = requests.post(url, json=data)

# Check the status code of the response
if response.status_code == 200:
    print("Token redeemed successfully.")
    # Process the response as needed
    print(response.json())
else:
    print(f"Failed to redeem token. Status code: {response.status_code}")
    print(response.text)
