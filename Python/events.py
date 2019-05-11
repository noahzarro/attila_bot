import datetime
import time


class TimedEvent:
    def __init__(self, weekday, hour, minute, callback, arg):
        self.due = datetime.timedelta(days=weekday, hours=hour, minutes=minute)
        self.callback = callback
        self.arg = arg

    def wait(self):
        now = datetime.datetime.today()
        base_monday = now - datetime.timedelta(days=now.weekday(), hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
        time_due = base_monday + self.due
        if time_due < now:
            time_due += datetime.timedelta(days=7)
        print("Due at: ", time_due)
        time_to_sleep = (time_due - datetime.datetime.today()).total_seconds()
        print("Sleep now for: ", time_to_sleep, " seconds.")
        time.sleep(time_to_sleep)
        self.callback(self.arg)


def get_next_saturday():
    now = datetime.datetime.today()
    base_monday = now - datetime.timedelta(days=now.weekday(), hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
    next_saturday = base_monday + datetime.timedelta(days=5)
    if now.weekday() == 5:
        next_saturday += datetime.timedelta(days=7)
    return str(next_saturday.day) + "." + str(next_saturday.month) + "." + str(next_saturday.year)