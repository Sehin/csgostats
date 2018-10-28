import requests

class SteamAPI():
    steamApiToken = '39C7455BF6652A9A4DAACB1ABFFC1A54'
    CSGOToken = '730'
    playerToken = '76561198415404266'
    URL = 'http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/'  # ?appid=730&key=39C7455BF6652A9A4DAACB1ABFFC1A54&steamid=76561198415404266

    statValues = ('total_matches_played',
    'last_match_damage',
    'total_mvps',
    'total_rounds_map_de_inferno',
    'total_rounds_map_de_dust2',
    'total_rounds_map_de_nuke',
    'total_rounds_map_de_train',
    'total_rounds_map_de_cbble',
    'total_kills_enemy_blinded',
    'total_kills_headshot',
    'total_kills',
    'total_deaths',
    'last_match_kills',
    'last_match_deaths',
    'last_match_mvps',
    'total_matches_won')


    def __init__(self):
        pass

    def getGameStats(self, steamId):
        res = dict()
        url = self.URL + '?appid={}&key={}&steamid={}'.format(self.CSGOToken, self.steamApiToken, steamId)
        answer = requests.get(url)
        for i in answer.json()["playerstats"]["stats"]:
            if (i["name"] in self.statValues):
                res.update({i["name"]: i["value"]})
        return res

    def isSteamProfileOpen(self, steamId):
        url = self.URL + '?appid={}&key={}&steamid={}'.format(self.CSGOToken, self.steamApiToken, steamId)
        answer = requests.get(url).json()
        if answer == {}:
            return False
        else:
            return True
