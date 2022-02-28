import pprint
import requests

playlist_map = {
    10: '1v1',
    11: '2v2',
    13: '3v3',
    27: 'Hoops',
    28: 'Rumble',
    29: 'Dropshot',
    30: 'Snow Day',
    34: 'Tournaments',
    0: 'Unranked',
}

translate_epic_id = {
    "Kumpy": "Kump (Steam kumpass_skater)",
    "LowEar353": "Biz Uzi Horizontal (Steam imkumpy)",
    "StrongHyena886": "Boost Willis (Steam itskumpy)",
    "MrKumpy": "MrKumpy (Epic lebergarrett@gmail.com)",
    "MrKump": "MrKump (Epic ksk.garrett@gmail.com)",
}


def main():
    epic_ids = ["Kumpy", "LowEar353", "StrongHyena886", "MrKump", "MrKumpy"]
    url = "https://api.tracker.gg/api/v2/rocket-league/standard/profile/epic/"
    account_map = {}

    for account in epic_ids:
        account_url = url + account
        print(account_url)
        json_stats = get_stats(account_url)

        returned_username = json_stats["platformInfo"]["platformUserHandle"]
        translated_username = translate_epic_id[account]
        playlist_ratings = get_ratings(json_stats)
        account_map[account] = playlist_ratings

        print("Returned Username:   " + returned_username)
        print("Translated Username: " + translated_username)
        print(playlist_ratings)
        print()

    lowest_rank_map = find_lowest_rank(account_map)
    translated_lowest_rank_map = translate_usernames(lowest_rank_map)

    print("Lowest Ranked account in each playlist:")
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(translated_lowest_rank_map)


def get_stats(url):
    # Headers required to receive a response from server
    stats = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0"
    })
    json_stats = stats.json() if stats and stats.status_code == 200 else None

    return json_stats["data"]


def get_playlist_data(json_stats, playlist_id):
    return json_stats["segments"][playlist_id]


def get_ratings(json_stats):
    rating_map = {}

    # Must iterate through predefined playlist map in case account hasn't played playlist before
    for playlist in playlist_map:
        playlist_name = playlist_map[playlist]

        # Check returned stats for the playlist
        for returned_playlist in json_stats["segments"]:
            # Ignores the first item which includes lifetime stats
            if returned_playlist['type'] != 'playlist':
                continue

            returned_playlist_name = playlist_map[returned_playlist['attributes']['playlistId']]

            # If present, add data
            if playlist_name == returned_playlist_name:
                rating_map[returned_playlist_name] = returned_playlist['stats']['rating']['value']
                break

        # If no rating was pulled back, account is fresh, giving 600 mmr
        if playlist_name not in rating_map:
            rating_map[playlist_name] = 600

    return rating_map


def find_lowest_rank(account_map):
    lowest_rank_map = {}  # {'1v1': MrKump, '2v2': MrKumpy, etc}

    for account in account_map:
        for playlist in account_map[account]:
            # Base case, all playlists will be listed
            if playlist not in lowest_rank_map:
                lowest_rank_map[playlist] = account

            # Pull data to run comparisons against
            compare_account = lowest_rank_map[playlist]
            compare_rating = account_map[compare_account][playlist]

            # Compare the ratings, if lower, replace value in map
            rating = account_map[account][playlist]
            if rating < compare_rating:
                lowest_rank_map[playlist] = account

    return lowest_rank_map


def translate_usernames(lowest_rank_map):
    translated_lowest_rank_map = {}

    for playlist in lowest_rank_map:
        translated_user = translate_epic_id[lowest_rank_map[playlist]]
        translated_lowest_rank_map[playlist] = translated_user

    return translated_lowest_rank_map


def debug_response(json_stats):
    for item in json_stats:
        # shows the returned items from api hit
        print(item)

        for sub_item in json_stats[item]:
            print("    ", end="")
            print(sub_item)


if __name__ == '__main__':
    main()
