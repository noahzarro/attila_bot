import requests
import datetime
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import logging
import json
import events
import copy

# activity Stuff
activity = []
activity_atributes = ["Stufe", "Datum", "Typ", "Zeit", "Ort", "Mitnehmen", "Spezielles"]
to_change = {}
standard_attribute = {"Stufe": "Biber", "Typ": "Übung", "Datum": "df", "Zeit": "14:00 - 16:00", "Ort":  "Pfadiheim", "Mitnehmen":  "", "Spezielles": ""}

# load activity
with open("activity.json","r") as read_file:
    activity = json.load(read_file)

# Bot Stuff
telegramBot = 0
chat_ids = set()

# next message
next_message = {}

# load people
with open("people.json","r") as read_file:
    people = json.load(read_file)

# create default person
dummy_person = {"name":"anonymous", "level":"NULL", "Mo": "Nein", "Do": "Ja", "Fr": "Nein", "Sa": "Nein", "ID":""}

# create Bot
with open("token.json","r") as read_file:
    TOKEN = json.load(read_file)[0]
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def write_people():
    with open("people.json", "w") as write_file:
        json.dump(people, write_file)


def change_person_value(id, key, value):
    i = 0
    id = str(id)
    while i<len(people):
        if people[i]["ID"] == id:
            people[i][key] = value
        i += 1
    write_people()
    print(people)


def get_person_value(id, key):
    id = str(id)
    for person in people:
        if person["ID"] == id:
            return person[key]
    return None


def info(bot, update):
    print(update.message.chat_id)
    name = get_person_value(update.message.chat_id, "name")
    print(name)
    level = get_person_value(update.message.chat_id, "level")
    print(level)
    mo = get_person_value(update.message.chat_id, "Mo")
    do = get_person_value(update.message.chat_id, "Do")
    fr = get_person_value(update.message.chat_id, "Fr")
    sa = get_person_value(update.message.chat_id, "Sa")
    info = "<b>Info:</b>\n\n<b>Name: </b>" + name + "\n<b>Stufe: </b>" + level + "\n<b>Mo: </b>" + mo + "\n<b>Do: </b>" + do + "\n<b>Fr: </b>" + fr + "\n<b>Sa: </b>" + sa
    bot.send_message(chat_id=update.message.chat_id, text=info, parse_mode="HTML")


def settings(bot, update):
    keyboard = []
    row1 = []
    row1.append(InlineKeyboardButton("Name", callback_data="{} {} {}".format("settings", update.message.from_user.id, "Name")))
    row1.append(InlineKeyboardButton("Stufe", callback_data="{} {} {}".format("settings", update.message.from_user.id, "Stufe")))
    row1.append(InlineKeyboardButton("Erinnerung", callback_data="{} {} {}".format("settings", update.message.from_user.id, "Erinnerung")))
    keyboard.append(row1)
    bot.send_message(chat_id=update.message.chat_id,text = "Einstellungen" ,reply_markup = InlineKeyboardMarkup(keyboard))


def start(bot, update):
    id = str(update.message.chat_id)
    print(id)
    if get_person_value(id, "ID") is None:
        bot.send_message(chat_id=update.message.chat_id, text="Willkommen beim Attilabot")
        print(id + " joined")
        dummy_person["ID"] = id
        people.append(dummy_person)
        write_people()
        return

    bot.send_message(chat_id=update.message.chat_id, text="Willkommen zurück")


def inline_handler(bot, update):
    query = update.callback_query

    action = query.data.split(" ")[0]
    user = query.data.split(" ")[1]
    value = query.data.split(" ")[2]
    arg = query.data[len(action) + len(user) + len(value) + 3:]

    bot.deleteMessage(chat_id=query.message.chat_id, message_id=query.message.message_id)

    if action == "settings":
        print(value)
        if value == "Name":
            bot.send_message(chat_id=query.message.chat_id, text="Wie ist dein Name?")
            next_message[query.message.chat_id] = "Name"

        if value == "Stufe":
            keyboard = []
            row1 = []
            row1.append(InlineKeyboardButton("Biber", callback_data="{} {} {}".format("level", query.message.chat_id, "Biber")))
            row1.append(InlineKeyboardButton("Wölfe", callback_data="{} {} {}".format("level", query.message.chat_id, "Wölfe")))
            row1.append(InlineKeyboardButton("Pfader", callback_data="{} {} {}".format("level", query.message.chat_id, "Pfader")))
            keyboard.append(row1)
            bot.send_message(chat_id=query.message.chat_id, text="Stufe wählen", reply_markup=InlineKeyboardMarkup(keyboard))

        if value == "Erinnerung":
            keyboard = []
            row1 = []
            row2 = []
            row1.append(InlineKeyboardButton("Mo", callback_data="{} {} {}".format("reminder_day", query.message.chat_id, "Mo")))
            row1.append(InlineKeyboardButton("Do", callback_data="{} {} {}".format("reminder_day", query.message.chat_id, "Do")))
            row2.append(InlineKeyboardButton("Fr", callback_data="{} {} {}".format("reminder_day", query.message.chat_id, "Fr")))
            row2.append(InlineKeyboardButton("Sa", callback_data="{} {} {}".format("reminder_day", query.message.chat_id, "Sa")))

            keyboard.append(row1)
            keyboard.append(row2)
            bot.send_message(chat_id=query.message.chat_id, text="Tag wählen", reply_markup=InlineKeyboardMarkup(keyboard))
    if action == "level":
        print(value)
        bot.send_message(chat_id=query.message.chat_id, text="Deine Stufe ist nun: {}".format(value))
        change_person_value(query.message.chat_id, "level", value)

    if action == "reminder_day":
        print(value)
        keyboard = []
        row1 = []
        row1.append(InlineKeyboardButton("Ja", callback_data="{} {} {} {}".format("decision_day", query.message.chat_id, value, "Ja")))
        row1.append(InlineKeyboardButton("Nein", callback_data="{} {} {} {}".format("decision_day", query.message.chat_id, value, "Nein")))
        keyboard.append(row1)
        bot.send_message(chat_id=query.message.chat_id, text="Erinnere am " + value + "?", reply_markup=InlineKeyboardMarkup(keyboard))

    if action == "decision_day":
        print(arg)
        if arg == "Ja":
            print("Ok, ich erinnere dich am ", value)
            bot.send_message(chat_id=query.message.chat_id, text="Ok, ich erinnere dich am " + value)
            change_person_value(query.message.chat_id, value, arg)

        if arg == "Nein":
            print("Ok, ich erinnere dich am ", value, " nicht mehr")
            bot.send_message(chat_id=query.message.chat_id, text="Ok, ich erinnere dich am " + value + " nicht mehr")
            change_person_value(query.message.chat_id, value, arg)

    if action == "change_all_activities":
        to_change[query.message.chat_id] = copy.deepcopy(activity_atributes)
        to_change[query.message.chat_id].remove("Stufe")

        attribute = to_change[query.message.chat_id].pop(0)
        keyboard = []
        row = []
        row.append(InlineKeyboardButton(standard_attribute[attribute], callback_data="{} {} {} {}".format("change_activity_atribute", query.message.chat_id, standard_attribute[attribute], attribute)))
        row.append(InlineKeyboardButton("Eingeben", callback_data="{} {} {} {}".format("change_activity_atribute", query.message.chat_id, "Eingeben", attribute)))
        row.append(InlineKeyboardButton("Abbrechen", callback_data="{} {} {} {}".format("change_activity_atribute", query.message.chat_id, "Abbrechen", attribute)))
        keyboard.append(row)

        bot.send_message(chat_id=query.message.chat_id, text=attribute, reply_markup=InlineKeyboardMarkup(keyboard))

    if action == "change_activity_atribute":
        if value == "Abbrechen":
            # could reset to_change, but does not matter (hopefully)
            return

        if value == "Eingeben":
            next_message[query.message.chat_id] = "{} {}".format("Attribut", arg)
            return

        if len(to_change[query.message.chat_id]) > 0 and value != "Abbrechen" and value != "Eingeben":
            print("change last activity")  # change last activity



            attribute = to_change[query.message.chat_id].pop(0)
            keyboard = []
            row = []
            row.append(InlineKeyboardButton(standard_attribute[attribute], callback_data="{} {} {} {}".format("change_activity_atribute", query.message.chat_id, standard_attribute[attribute], attribute)))
            row.append(InlineKeyboardButton("Eingeben", callback_data="{} {} {} {}".format("change_activity_atribute", query.message.chat_id, "Eingeben", attribute)))
            row.append(InlineKeyboardButton("Abbrechen", callback_data="{} {} {} {}".format("change_activity_atribute", query.message.chat_id, "Abbrechen", attribute)))
            keyboard.append(row)

            bot.send_message(chat_id=query.message.chat_id, text=attribute, reply_markup=InlineKeyboardMarkup(keyboard))


def reminder(weekday):
    print("reminder active")
    for person in people:
        print(person["ID"], " ", person[weekday])
        if person[weekday] == "Ja":
            updater.bot.send_message(chat_id=person["ID"], text="Reminder")


def insult():
    return "Vollasichlotz"


def get_level(id):
    id = str(id)
    for person in people:
        if person["ID"] == id:
            print(person["level"])
            return person["level"]


def set_activity_element(level, key, value):
    i = 0
    while i<len(activity):
        if activity[i]["Stufe"] == level:
            activity[i][key] = value
            return
        i += 1


def get_activity_element(level, key):
    for levels in activity:
        if levels["Stufe"] == level:
            return levels[key]


def get_activity(level):
    activity_text = "<b>Info:</b>\n\n"
    for atribute in activity_atributes:
        activity_text += "<b>" + atribute + ": </b>" + get_activity_element(level, atribute) + "\n"

    return activity_text


def current(bot, update):
    level = get_person_value(update.message.chat_id, "level")
    if level is not None:
        bot.send_message(chat_id=update.message.chat_id, text=get_activity(level), parse_mode="HTML")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Zerst mit \start registriere, " + insult())


def change_activity(bot, update):
    current(bot, update)
    keyboard = []
    row1 = []
    row1.append(InlineKeyboardButton("Alle", callback_data="{} {} {}".format("change_all_activities", update.message.chat_id, "alle")))
    keyboard.append(row1)
    for atribute in activity_atributes:
        if atribute != "Stufe":
            row = list()
            row.append(InlineKeyboardButton(atribute, callback_data="{} {} {}".format("change_activity_atribute", update.message.chat_id, atribute)))
            keyboard.append(row)
    bot.send_message(chat_id=update.message.chat_id, text="Was möchtest du bearbeiten?", reply_markup=InlineKeyboardMarkup(keyboard))


def answer_handler(bot, update):
    print("gotter")
    print(next_message[update.message.chat_id])
    if not update.message.chat_id in next_message:
        bot.send_message(chat_id=update.message.chat_id, text="Verstandi nöd, " + insult())
        return

    # get type of next expected answer
    data = next_message[update.message.chat_id]

    command = data.split(" ")[0]
    arg = data.split(" ")[1]

    print(command)

    # reset type of next expected answer
    next_message[update.message.chat_id] = ""

    if command == "Name":
        print("Name: {}".format(update.message.text))
        change_person_value(update.message.chat_id, "name", update.message.text)
        bot.send_message(chat_id=update.message.chat_id, text="Name geändert zu: {}".format(update.message.text))
        if update.message.text == "Noah" or update.message.text == "Calmo":
            bot.send_message(chat_id=update.message.chat_id, text="Das ist denn ein schöner Name, Gratulation!")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Was für ein hässlicher Name! " + insult() + "!")

    elif command == "Attribut":
        print("gatter")
        set_activity_element(get_level(update.message.chat_id), arg, update.message.text)
        print("gitter")
        # issue new request
        if len(to_change[update.message.chat_id]) > 0:
            attribute = to_change[update.message.chat_id].pop(0)
            keyboard = []
            row = []
            row.append(InlineKeyboardButton(standard_attribute[attribute], callback_data="{} {} {}".format("change_activity_atribute", update.message.chat_id, standard_attribute[attribute], attribute)))
            row.append(InlineKeyboardButton("Eingeben", callback_data="{} {} {}".format("change_activity_atribute", update.message.chat_id, "Eingeben", attribute)))
            row.append(InlineKeyboardButton("Abbrechen", callback_data="{} {} {}".format("change_activity_atribute", update.message.chat_id, "Abbrechen", attribute)))
            keyboard.append(row)

            bot.send_message(chat_id=update.message.chat_id, text=attribute, reply_markup=InlineKeyboardMarkup(keyboard))

    else:
        bot.send_message(chat_id=update.message.chat_id, text="Verstandi nöd " + insult() + ", benutz en Command")


# register commands
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('settings', settings))
dispatcher.add_handler(CommandHandler('info', info))
dispatcher.add_handler(CommandHandler('current', current))
dispatcher.add_handler(CommandHandler('change', change_activity))


# register inline query handler
updater.dispatcher.add_handler(CallbackQueryHandler(inline_handler))

# register handler for plain messages
dispatcher.add_handler(MessageHandler(Filters.text, answer_handler))

telegramBot = updater.bot
updater.start_polling()

reminder_Mo = events.TimedEvent(0, 10, 0, reminder, "Mo")
reminder_Do = events.TimedEvent(1, 17, 15, reminder, "Do")
reminder_Fr = events.TimedEvent(4, 17, 0, reminder, "Fr")
reminder_Sa = events.TimedEvent(5, 11, 0, reminder, "Sa")

print("bot started")

while True:
    reminder_Do.wait()
    reminder_Fr.wait()
    reminder_Sa.wait()
