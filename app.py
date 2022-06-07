import pip
import json
import sys

import requests
from pprint import pprint
from os import getenv

API_URL = 'https://osu.ppy.sh/api/v2'
TOKEN_URL = 'https://osu.ppy.sh/oauth/token'

# osu auth
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
        'limit': 100
    }
    user_id = 7562902
    # Fetch user statistics
    user = requests.get(f'{API_URL}/users/{user_id}/osu', params=params, headers=headers).json()
    user_stats = user.get('statistics')
    pprint(user_stats)
    print("USER STATS")
    print(f"pp: {user_stats.get('pp')}")
    print(f"Hit Acc: {user_stats.get('hit_accuracy')}")
    print(f"Play Count: {user_stats.get('play_count')}")

    print("TOP 100 SCORE ANALYSIS")

    # Fetch best scores for a user
    top100 = requests.get(f'{API_URL}/users/{user_id}/scores/best', params=params, headers=headers).json()

    # Weighed frequency of most-used modifications in top 100 plays
    mods_total = {"NM":0,"HD":0,"HR":0,"DT":0,"FL":0}

    # Weighted average map length
    average_length = 0

    # Weighted average map BPM
    average_bpm = 0

    # This value is the maximum possible top 100 weighting. Divide weighted values by this to find the average.
    weight_sum = 19.881589415
    
    for i in range(0, 100):
        play = top100[i]
        # same weighting as pp
        weight = 0.95**i

        ## Most Used Mods
        mods = play.get('mods')
        if(len(mods) == 0):
            mods_total["NM"] += weight
        for mod in mods:
            # Convert NC to DT
            if(mod == "NC"):
                mods_total["DT"] += weight
            elif mod in mods_total:
                mods_total[mod] += weight

        ## Average Length/BPM
        map = play.get('beatmap')
        if("DT" in mods or "NC" in mods):
            average_length += map.get('hit_length')*weight/1.5
            average_bpm    += map.get('bpm')*weight*1.5
        else:
            average_length += map.get('hit_length')*weight
            average_bpm    += map.get('bpm')*weight

    for i in mods_total:
        print(f"{i}: {round(mods_total[i]/weight_sum, 2)} | ", end = '')
    print(f"\nWeighted Map Length: {round(average_length/weight_sum,2)}")
    print(f"Weighted Map BPM:    {round(average_bpm/weight_sum,2)}")

if __name__ == '__main__':
    main()