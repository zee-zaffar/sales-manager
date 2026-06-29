import json
import os
import requests

def save_tokens(access_token, refresh_token, filename="tokens.json"):
    tokens = {
        "access_token": access_token,
        "refresh_token": refresh_token
    }
    with open(filename, "w") as f:
        json.dump(tokens, f)

def load_tokens(filename="tokens.json"):
    with open(filename, 'r') as f:
        tokens = json.load(f)
        return tokens.get("access_token"), tokens.get("refresh_token")

def get_tokens(client_id, refresh_token)->str:
    url = "https://api.etsy.com/v3/public/oauth/token"
    headers = {
       "Accept": "application/json",
       "Content-Type": "application/json"
    }
   
    data = {
        "grant_type": "refresh_token",
        "client_id": f"{client_id}",
        "refresh_token": f"{refresh_token}"
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        # response.raise_for_status()
        print(f"Response Text: {response.text}")
        if response.status_code == 200:
           data = response.json()
           save_tokens(data['access_token'], data['refresh_token'])
           return data['access_token']
    except requests.RequestException as e:
        print(f"Error: {e}")
        return {"error": str(e)} 
