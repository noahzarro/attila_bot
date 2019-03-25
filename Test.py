import requests
import datetime
import time
from telegram.ext import Updater
from telegram.ext import CommandHandler
import logging
import json

# Bot Stuff

telegramBot = 0
chat_ids = set()

# load people
with open("people.json","r") as read_file:
    people = json.load(read_file)

# create default person
dummy_person = {"name":"anonymous", "level":"NULL", "Mo": False, "Do": True, "Fr": False, "Sa": False, "ID":""}

# create Bot
with open("token.json","r") as read_file:
    TOKEN = json.load(read_file)[0]
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def change_person_value(id, key, value):
    for person in people:
        if person["ID"] == id:
            person[key] = value


def get_person_value(id, key):
    for person in people:
        if person["ID"] == id:
            return person[key]
    return None


def write_people():
    with open("people.json", "w") as write_file:
        json.dump(people, write_file)


def start(bot, update):
    id = str(update.message.chat_id)
    if get_person_value(id, "ID") is None:
        bot.send_message(chat_id=update.message.chat_id, text="Willkommen beim Attilabot")
        print(id + " joined")
        dummy_person["ID"] = id
        people.append(dummy_person)
        write_people()
        return

    bot.send_message(chat_id=update.message.chat_id, text="Willkommen zurück")


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

telegramBot = updater.bot
updater.start_polling()

print("bot started")

while True:
    continue