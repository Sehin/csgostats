from DBWorker import DBWorker
from SteamAPI import SteamAPI
from TelegramBot import TelegramBot
from DataWorker import DataWorker
from threading import Thread
from multiprocessing import Process
import time

def main():
    dw = DataWorker()
    bot = TelegramBot(dw)
    #oeoe
    thr1 = Thread(target=bot.polling)
    thr2 = Thread(target=dw.polling)
    thr1.start()
    thr2.start()

def test():
    def func1():
        for i in range(10):
            print('0')
            time.sleep(0.5)
    def func2():
        for i in range(10):
            print('1')
            time.sleep(0.75)
    p1 = Process(target=func1())
    p2 = Process(target=func2())

if __name__=='__main__':
    #test()
    main()