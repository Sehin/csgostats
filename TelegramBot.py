import requests
import DBWorker
import time
import SteamAPI
from datetime import datetime
from DataWorker import DataWorker

class Message:
    text = ""
    chatId = ""
    updateId = ""
    def __init__(self, text, chatId, updateId):
        self.text = text
        self.chatId = chatId
        self.updateId = updateId

class TelegramBot():
    URL = 'https://api.telegram.org/bot'
    token = '775436706:AAHwnDNL0ieix3KXVHrSUO2-bg8Nl1628zI'
    offsetId = 1
    repeatRequestTime = 1

    usersState = []
    dbWorker = DBWorker.DBWorker()
    users = dbWorker.getUsers()
    steamApi = SteamAPI.SteamAPI()

    def __init__(self, dataWorker):
        self.dataWorker = dataWorker

    def getUpdates(self):
        url = self.URL + self.token + '/getupdates?offset=' + str(self.offsetId)
        answer = requests.get(url)
        return answer.json()

    def getMessages(self):
        # take last msg update id and set it to offsetId + 1
        data = self.getUpdates()
        messages = list()
        for message in data["result"]:
            messages.append(Message(message["message"]["text"],
                                        str(message["message"]["chat"]["id"]),
                                        message["update_id"]))
        if data["result"] != []:
            self.offsetId = int(data["result"][-1]["update_id"]) + 1
        return messages

    def sendMessage(self, chat_id, text):
        url = self.URL + self.token + '/sendmessage?chat_id={}&text={}'.format(chat_id, text)
        requests.get(url)

    def sendMsgToAllUsers(self, text, users):
        for user in users:
            self.sendMessage(user, text)

    def parseMessage(self, message):
        # Проход по листу состояния пользователей
        state = self._getUserFromStateList(message.chatId)
        if (state['state']==None):
            if message.text == '/start':
                self.sendMessage(message.chatId, 'Welcome to CSGOStats!\nTo recieve your statistics after every game:\n1. Make your steam profile privacy \'Open\'\n2. Send me your Steam id (/steamid command)\nIf you wanna stop - write me command /stop')
            if message.text == '/steamid':
                user = self._getChatIdFromList(message.chatId)
                if (user != None):
                    self.sendMessage(message.chatId, 'You are already in our system! Your steam id - {}. Now your state is - {}.\nYou can /stop or /begin.'.format(user['steamToken'], 'active' if user['isActive'] == 1 else 'inactive'))
                else:
                    self.sendMessage(message.chatId, 'Ok, now send me your Steam id!')
                    state['state'] = 'isSteamCommandWait'
                    pass
            if message.text == '/stop':
                user = self.dbWorker.getUser(message.chatId)
                if user == None:
                    self.sendMessage(message.chatId, 'Join us first.\nTry command /start')
                elif user['isActive'] == 0:
                    self.sendMessage(message.chatId, 'Hey, we already stop.\nIf you wanna begin, try /begin')
                else:
                    self.dbWorker.setUserIsActive(0, user)
                    self.users = self.dbWorker.getUsers()
                    self.sendMessage(message.chatId, 'Ok, we stop send you statistic.\nUse /begin to start!')
            if message.text == '/begin':
                user = self.dbWorker.getUser(message.chatId)
                if user == None:
                    self.sendMessage(message.chatId, 'Join us first.\nTry command /start')
                elif user['isActive'] == 1:
                    self.sendMessage(message.chatId, 'Hey, we already send you statistic.')
                else:
                    self.dbWorker.setUserIsActive(1, user)
                    self.users = self.dbWorker.getUsers()
                    self.sendMessage(message.chatId, 'Ok, we begin to send you statistic.')


        # Часть парсинга части, когда пользователь вводит steamid
        elif state['state'] == 'isSteamCommandWait':
            print('steamid: ' + message.text)
            # Проверка является ли аккаунт открытым или
            if not self.steamApi.isSteamProfileOpen(message.text):
                self.sendMessage(message.chatId, 'OMG! Shit happens :-(\nCheck your profile settings (it privacy should be \'Open\') or check your Steam id right.')
            else:
                self.sendMessage(message.chatId, 'All right!\nNow you will receive your game statistics after every game!\nIf you wanna stop - write me command /stop')
                user = {'isActive': 1, 'steamtoken': message.text, 'chat_id': message.chatId}
                self.dbWorker.insertUsers(user)
                stat = self.steamApi.getGameStats(user['steamtoken'])
                self.dbWorker.addStat(stat, user['steamtoken'])
            state['state'] = None

    '''
    Функция возвращает состояние для конкретного пользователя
    '''
    def _getUserFromStateList(self, chat_id):
        for state in self.usersState:
            if (chat_id == state['chat_id']):
                return state
        state = {'chat_id': chat_id, 'state': None}
        self.usersState.append(state)
        return state

    def _getChatIdFromList(self, chat_id):
        for user in self.users:
            if user['chatId'] == chat_id:
                return user
        return None

    def sendStatToUser(self, stat):
        #self.sendMessage(stat[0], 'Wow, we have new stat for you! Listen..')
        strToSend = ''
        strToSend += str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + '\n'
        if (stat[1]['total_matches_won'] > 0):
            strToSend += 'You win! Good work man!\n'
        else:
            strToSend += 'You loose :(\n'
        strToSend += 'K/D: {}/{}\n'.format(stat[1]['total_kills'], stat[1]['total_deaths'])
        strToSend += 'MVP: {}\n'.format(stat[1]['total_mvps']) if stat[1]['total_mvps'] > 0 else ''
        strToSend += 'Headshot kills: {}\n'.format(stat[1]['total_kills_headshot'])
        strToSend += 'Enemy blinded kills: {}\n'.format(stat[1]['total_kills_enemy_blinded']) \
            if stat[1]['total_kills_enemy_blinded'] > 0 else ''
        strToSend += 'Match damage: {}\n'.format(stat[1]['last_match_damage'])

        # for rec in stat[1]:
        #     strToSend += rec + ' ' + str(stat[1][str(rec)]) + ' ;'
        self.sendMessage(stat[0], strToSend)
        pass

    def polling(self):
        while 1:
            print('start cycle TB')
            print(self.dataWorker.checker)
            for message in self.getMessages():
                # userLogger.info("User " + str(message.chatId) + " send to bot: " + str(message.text))
                # -----------------------------
                # ОСНОВНАЯ ОБРАБОТКА СОБЩЕНИЙ!!!
                # -----------------------------
                print(message.text)
                self.parseMessage(message)
                '''
                # Все, что связано с подпиской
                q = checkPasswordInput(message.chatId, message.text, users)
                if q != None:
                    users.add(q)
                    dbworker.insertUser(q)
                    # infoLogger.info("User add to subscribe " + q)

                # Все, что связано с отпиской
                q = checkStopInput(message.chatId, message.text, users)
                if q != None:
                    users.remove(q)
                    dbworker.removeUser(q)
                    # infoLogger.info("User remove from subscribe " + q)

            # Основной метод рассылки
            sendIncidentsToAllUsers(users)
            '''


            #print(len(self.dataWorker.statUpdates))
            print('TB: ' + str(self.dataWorker.statUpdates))
            while not self.dataWorker.statUpdates == []:
                if len(self.dataWorker.statUpdates) > 0:
                    stat = self.dataWorker.statUpdates.pop()
                    self.sendStatToUser(stat)

            # for stat in self.dataWorker.statUpdates:
            #     self.sendStatToUser(stat)

            time.sleep(self.repeatRequestTime)
