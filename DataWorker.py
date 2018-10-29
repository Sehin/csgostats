import time
from DBWorker import DBWorker
from SteamAPI import SteamAPI

class DataWorker():
    repeatRequestTime = 10
    dbWorker = DBWorker()
    steamAPI = SteamAPI()
    statUpdates = []
    checker = 0
    def __init__(self):
        pass

    def polling(self):
        # Раз в repeatRequestTime пройтись по пользователям
        # Для каждого пользователя:
        # Получить актуальную статистику из SteamAPI
        # Сравнить парметр total_matches_played в актуальной статистике с последней записью в БД
        # Если она различна - то получить дельту всех полей
        # Сформировать сообщение для пользователя, отдать в TelegramBot?

        # ''' Test block '''
        # stat = self.steamAPI.getGameStats('76561198415404266')
        # self.statUpdates.append(['205612692', stat])

        while 1:
            #print('start cycle DW')
            #print(self.statUpdates)
            users = self.dbWorker.getActiveUsers()
            for user in users:
                stat = self.steamAPI.getGameStats(user['steamToken'])
                matchesPlayedLast = self.dbWorker.getLastTotalMatchPlayed(user['steamToken'])
                if stat['total_matches_played'] > matchesPlayedLast[0]:
                    lastMatchStat = self.dbWorker.getStat(matchesPlayedLast[1])
                    # СРАВНИИТЬ!
                    # ОДИНАКОВЫЕ КЛЮЧИ, НО РАЗНЫЕ ЗНАЧЕНИЯ!!!
                    delta = dict()
                    for rec_stat in stat:
                        #print('Stat {}\nNew stat : {}\nOld stat : {}'.format(rec_stat, stat[rec_stat], lastMatchStat[rec_stat]))
                        delta.update({rec_stat: stat[rec_stat]-lastMatchStat[rec_stat]})
                    delta['last_match_damage'] = stat['last_match_damage']
                    self.statUpdates.append([user['chatId'], delta])
                    self.dbWorker.addStat(stat, user['steamToken'])
                    print('DW: ' + str(self.statUpdates))
                    #print(self.statUpdates)


            # stat = self.steamAPI.getGameStats('76561198415404266')
            # self.statUpdates.append(['205612692', stat])

            time.sleep(self.repeatRequestTime)
