# import os
# import requests
# import json

# from .interfaces import AccessTokenResponse

# def get_refresh_token(client_id, refresh_token)-> AccessTokenResponse | dict:
#     url = "https://api.etsy.com/v3/public/oauth/token"
#     headers = {
#        "Accept": "application/json",
#        "Content-Type": "application/json"
#     }
   
#     data = {
#         "grant_type": "refresh_token",
#         "client_id": f"{client_id}",
#         "refresh_token": f"{refresh_token}"
#     }

#     try:
#         response = requests.post(url, headers=headers, json=data)
#         # response.raise_for_status()
#         print(f"Response Text: {response.text}")
#         if response.status_code == 200:
#            data = response.json()
#            token = AccessTokenResponse(**data)
#            return token
#     except requests.RequestException as e:
#         print(f"Error: {e}")
#         return {"error": str(e)} 

# # Example usage:
# if __name__ == "__main__":
#     from dotenv import load_dotenv
#     load_dotenv()
#     import os

#     token_response = get_etsy_access_token(
#         client_id= "dxe8mdgsficst03cqeqzp6bf",
#         auth_code= os.getenv("ETSY_AUTH_CODE"),
#         code_verifier= os.getenv("ETSY_CODE_VERIFIER"),
#         redirect_uri= os.getenv("ETSY_REDIRECT_URI")
#     )
#     print(f"Token Response:{token_response}")