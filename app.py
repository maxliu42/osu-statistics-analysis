import requests
from pprint import pprint
from os import getenv

API_URL = 'https://osu.ppy.sh/api/v2'
TOKEN_URL = 'https://osu.ppy.sh/oauth/token'

def get_token():
    data = {
        'client_id': '15256',
        'client_secret': 'wxHlkr4WT3Y7pNycCSV60X0Rvgz0J2srwzzNqw0h',
        'grant_type': 'client_credentials',
        'scope': 'public'
    }

    response = requests.post(TOKEN_URL, data=data)

    return response.json().get('access_token')

def main():
    token = get_token()

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    params = {
        'mode': 'osu',
        'limit': 5
    }

    response = requests.get(f'{API_URL}/users/8676747/scores/best', params=params, headers=headers)
    pprint(response.json())


if __name__ == '__main__':
    main()