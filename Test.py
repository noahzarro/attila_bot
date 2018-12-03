import requests
import datetime
import time
from telegram.ext import Updater
from telegram.ext import CommandHandler
from bs4 import BeautifulSoup
import logging

page = requests.get("https://attila-teufen.weebly.com/")
print("Website loaded with code: " + str(page.status_code))

soup = BeautifulSoup(page.content,'html.parser')

subtitles=soup.find_all('h2')

for h2 in subtitles:
    if (h2.get_text()=="Biberstufe"):
        biber=h2

biberColum=biber.parent

spalten = biberColum.find_all('td',class_='wsite-multicol-col')
spalte = spalten[1]

block=spalte.find_all('font')[0]

data_start = str(block).find('>')
data_end = str(block).find('<',1)

data = str(block)[data_start+1:data_end]
print(data)
# data now ready

firstPointIndex = data.find('.')
secondPointIndex = data.find('.',firstPointIndex+1)

day = int(data[0:firstPointIndex])
month = int(data[firstPointIndex+1:secondPointIndex])
year_string = data[secondPointIndex+1:len(data)]
year = int(year_string)

if len(year_string)==2:
    year += 2000


print(day)
print(month)
print(year)

correct=0

now = datetime.datetime.now()

if datetime.datetime(year,month,day) >= now:
    correct = 1

# check day of the week

if now.weekday()<3 or now.weekday()==6:
    exit(0)

# Bot Stuff

telegramBot=0
chat_ids = set()

# load chats
subscribers = open("subscribers.txt","r")
for line in subscribers:
    chat_ids.add(int(line))

subscribers.close()

# create Bot
updater = Updater(token='542559791:AAGNLeMRv5qo0zSIpJ8aVUGEtl7-bN5KM5M')
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(bot,update):
    bot.send_message(chat_id=update.message.chat_id, text="Ur an fagit, bot aktiviert")
    chat_ids.add(update.message.chat_id)
    subscribers_write = open("subscribers.txt", "w")
    for id in chat_ids:
        subscribers_write.write(str(id))
    subscribers_write.close()


def end(bot,update):
    bot.send_message(chat_id=update.message.chat_id, text="Y u do this, ur an fagit")
    chat_ids.remove(update.message.chat_id)
    subscribers_write = open("subscribers.txt", "w")
    for id in chat_ids:
        subscribers_write.write(str(id))
    subscribers_write.close()


start_handler = CommandHandler('start',start)
dispatcher.add_handler(start_handler)

end_handler = CommandHandler('end',end)
dispatcher.add_handler(end_handler)

telegramBot = updater.bot
updater.start_polling()

time.sleep(5)

if telegramBot != 0:
    for chat_id in chat_ids:
        if correct==0:
            telegramBot.send_message(chat_id=chat_id, text="Die Webseite ist noch nicht aktuell, bitte aktualisieren")
        else:
            telegramBot.send_message(chat_id=chat_id, text="Die Webseite ist aktuell, gratuliere")
updater.stop()