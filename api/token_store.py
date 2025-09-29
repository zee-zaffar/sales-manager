import json
import os

def save_tokens(access_token, refresh_token, filename="tokens.json"):
    tokens = {
        "access_token": access_token,
        "refresh_token": refresh_token
    }
    with open(filename, "w") as f:
        json.dump(tokens, f)

def load_tokens(filename="tokens.json"):
    if not os.path.exists(filename):
        return None, None
    with open(filename) as f:
        tokens = json.load(f)
        return tokens.get("access_token"), tokens.get("refresh_token")
