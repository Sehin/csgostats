import mysql.connector
from datetime import datetime

class DBWorker():
    connection = mysql.connector.connect(user='root', password='root',
                                      host='localhost',
                                      database='csgostats',
                                      auth_plugin='mysql_native_password')
    def __init__(self):
        pass

    def addStat(self, stat, user_token):
        #with self.connection.cursor() as cursor:
        cursor = self.connection.cursor()
        sql = 'INSERT INTO `csgostats`.`stats` ' \
              '(`date`, `user_token`, `total_matches_played`,' \
              ' `total_mvps`, `last_match_damage`, `total_rounds_map_de_inferno`,' \
              ' `total_rounds_map_de_dust2`, `total_rounds_map_de_nuke`, `total_rounds_map_de_train`,' \
              ' `total_rounds_map_de_cbble`, `total_kills_enemy_blinded`, `total_kills_headshot`,' \
              ' `total_kills`, `total_deaths`, `last_match_kills`,' \
              ' `last_match_deaths`, `last_match_mvps`, `total_matches_won`) VALUES ' \
              '(\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\');'.format(
            datetime.now(), user_token, stat["total_matches_played"],
            stat["total_mvps"], stat["last_match_damage"], stat["total_rounds_map_de_inferno"],
            stat["total_rounds_map_de_dust2"], stat["total_rounds_map_de_nuke"], stat["total_rounds_map_de_train"],
            stat["total_rounds_map_de_cbble"], stat["total_kills_enemy_blinded"], stat["total_kills_headshot"],
            stat["total_kills"], stat["total_deaths"], stat["last_match_kills"],
            stat["last_match_deaths"], stat["last_match_mvps"], stat["total_matches_won"])
        cursor.execute(sql)
       # print(cursor.description)
        self.connection.commit()

    def getLastTotalMatchPlayed(self, steamId):
        cursor = self.connection.cursor()
        sql = 'select total_matches_played, idstats from csgostats.stats where user_token = '+str(steamId)+' and idstats = (select max(idstats) from csgostats.stats)'
        cursor.execute(sql)
        return cursor.fetchall()[0]

    def getUsers(self):
        users = []
        cursor = self.connection.cursor()
        sql = "select * from csgostats.users"
        cursor.execute(sql)
        data = cursor.fetchall()
        for rec in data:
            user_data = {'isActive': rec[0], 'steamToken': rec[1], 'chatId': rec[2]}
            users.append(user_data)
        return users

    def getActiveUsers(self):
        users = []
        cursor = self.connection.cursor()
        sql = "select * from csgostats.users where isactive=1"
        cursor.execute(sql)
        data = cursor.fetchall()
        for rec in data:
            user_data = {'isActive': rec[0], 'steamToken': rec[1], 'chatId': rec[2]}
            users.append(user_data)
        return users

    def insertUsers(self, user):
        cursor = self.connection.cursor()
        sql = "INSERT INTO `csgostats`.`users` (`isactive`, `steamtoken`, `chat_id`) VALUES ('{}', '{}', '{}');".format(user['isActive'], user['steamtoken'], user['chat_id'])
        cursor.execute(sql)
        self.connection.commit()

    def getUser(self, chat_id):
        cursor = self.connection.cursor()
        sql = "select * from csgostats.users where chat_id={};".format(chat_id)
        cursor.execute(sql)
        data = cursor.fetchall()
        for rec in data:
            user = {'isActive': rec[0], 'steamToken': rec[1], 'chatId': rec[2]}
            return user
        return None

    def getStat(self, idstats):
        columns = self.getColumns()

        cursor = self.connection.cursor()
        sql = "select * from csgostats.stats where idstats={};".format(idstats)
        cursor.execute(sql)
        data = cursor.fetchall()[0]
        res = dict()
        counter = 0
        for stat in data:
            res.update({columns[counter]: stat})
            counter += 1
        # Удаляю лишние значения, оставляю только голую статистику
        res.pop('idstats')
        res.pop('date')
        res.pop('user_token')
        return res

    def getColumns(self):
        cursor = self.connection.cursor()
        sql = "SHOW COLUMNS FROM csgostats.stats"
        cursor.execute(sql)
        res = []
        data = cursor.fetchall()
        for rec in data:
            res.append(rec[0])
        return res

    def setUserIsActive(self, isActive, user):
        cursor = self.connection.cursor()
        sql = "UPDATE `csgostats`.`users` SET `isactive` = '{}' WHERE (`chat_id` = '{}');".format(isActive, user['chatId'])
        cursor.execute(sql)
        self.connection.commit()
