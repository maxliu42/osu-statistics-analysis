import pip
import json

import requests

API_URL = 'https://osu.ppy.sh/api/v2'
TOKEN_URL = 'https://osu.ppy.sh/oauth/token'

# osu auth
def get_token():
    data = {
        'client_id': getenv('CLIENT_ID'),
        'client_secret': getenv('CLIENT_SECRET'),
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
    
    stat_needed = ['pp', 'play_count', 'play_time', 'total_hits', 'hit_accuracy']
    user_needed = ['id','username']

    # Faster to look up than to calculate
    weights = [1.0, 0.95, 0.9025, 0.85737, 0.81451, 0.77378, 0.73509, 0.69834, 0.66342, 0.63025, 0.59874, 0.5688, 0.54036, 0.51334, 0.48767, 0.46329, 0.44013, 0.41812, 0.39721, 0.37735, 0.35849, 0.34056, 0.32353, 0.30736, 0.29199, 0.27739, 0.26352, 0.25034, 0.23783, 0.22594, 0.21464, 0.20391, 0.19371, 0.18403, 0.17482, 0.16608, 0.15778, 0.14989, 0.1424, 0.13528, 0.12851, 0.12209, 0.11598, 0.11018, 0.10467, 0.09944, 0.09447, 0.08974, 0.08526, 0.08099, 0.07694, 0.0731, 0.06944, 0.06597, 0.06267, 0.05954, 0.05656, 0.05373, 0.05105, 0.04849, 0.04607, 0.04377, 0.04158, 0.0395, 0.03752, 0.03565, 0.03387, 0.03217, 0.03056, 0.02904, 0.02758, 0.0262, 0.02489, 0.02365, 0.02247, 0.02134, 0.02028, 0.01926, 0.0183, 0.01738, 0.01652, 0.01569, 0.01491, 0.01416, 0.01345, 0.01278, 0.01214, 0.01153, 0.01096, 0.01041, 0.00989, 0.00939, 0.00892, 0.00848, 0.00805, 0.00765, 0.00727, 0.00691, 0.00656, 0.00623]

    osu_csv = open("osu.csv", 'w')

    # Each page is 50 users. Interate over 200 pages total for data of top 10k users
    for page in range(80, 201): #201):
        rankings = requests.get(f'{API_URL}/rankings/osu/performance?page={page}', params=params, headers=headers).json()
        rankings = rankings.get('ranking')

        # Iterate over each of the 50 users on the page.
        for user in rankings:

            # Get info for current user on page
            user_info = user.get('user')
            user_id = user_info.get('id')

            # Get stats from ranking object
            for item in user_needed:
                osu_csv.write(str(user_info.get(item)) + ',')
            for item in stat_needed:
                osu_csv.write(str(user.get(item)) + ',')

            # Fetch user statistics for badges
            badges = len(requests.get(f'{API_URL}/users/{user_id}/osu', params=params, headers=headers).json().get('badges'))
            osu_csv.write(str(badges) + ',')

            # Fetch best scores for a user
            top100 = requests.get(f'{API_URL}/users/{user_id}/scores/best', params=params, headers=headers).json()

            # Weighed frequency of most-used modifications in top 100 plays
            mods_total = {"NM":0,"HD":0,"HR":0,"DT":0,"FL":0}

            # Weighted average map length
            average_length = 0

            # Weighted average map BPM
            average_bpm = 0

            # This value is the maximum possible top 100 weighting. Divide weighted values by this to find the average.
            weight_sum = 19.8816
            
            for i in range(0, min(100,len(top100))):
                play = top100[i]

                # Same weighting as pp
                weight = weights[i]

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

            osu_csv.write(str(average_bpm/weight_sum) + ',')

            for i in mods_total:
                osu_csv.write(str(mods_total[i]/weight_sum) + ',')

            osu_csv.write(str(average_length/weight_sum))
            osu_csv.write('\n')

if __name__ == '__main__':
    main()
