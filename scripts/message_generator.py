import requests
import json


API = "http://localhost:5000/messages"


for i in range(10):
    requests.post(API, json={"content": f"Message {i}"})