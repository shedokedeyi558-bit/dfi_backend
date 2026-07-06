import json

import requests

res = requests.get("https://jsonplaceholder.typicode.com")


res = requests.post(
    "https://jsonplaceholder.typicode.com/posts", json={"title": "text"}
)

print(res.status_code)


"""
print(f"Status Code: {res.status_code}")
print(res.text)
print(f"Response (JSON): {res.json()}")
print()


"""
