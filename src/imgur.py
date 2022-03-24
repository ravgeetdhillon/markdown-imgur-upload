import os
import requests
from dotenv import load_dotenv

load_dotenv()


def upload_to_imgur(image_path):
    print(image_path)
    url = 'https://api.imgur.com/3/image'
    files = [('image', (image_path, open(image_path, 'rb')))]
    headers = {'Authorization': f"Client-ID {os.getenv('CLIENT_ID')}"}
    response = requests.request("POST", url, headers=headers, files=files)
    return response.json()['data']['link']
