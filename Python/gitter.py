import events

def gitter(*args):
    print("gitter gatter gotter")

new_event = events.TimedEvent(1, 16, 28, gitter, None)
new_event.wait()