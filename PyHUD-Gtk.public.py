from gi.repository import GtkClutter
GtkClutter.init([])
from gi.repository import Clutter, GObject, Gtk, Gdk
import sys
from urllib import urlopen
from datetime import datetime, timedelta
from elementtree.ElementTree import parse
#from xml.etree.ElementTree import parse
class GenericStage(GtkClutter.Embed):

    def __init__(self):
        super(GenericStage, self).__init__()
        self.stage = self.get_stage()
        self.stage.set_size(320, 240)
        self.stage.connect('destroy', lambda x: Clutter.main_quit())

class TimeStage(GenericStage):

    def __init__(self):
        super(TimeStage, self).__init__()
        self.stage.connect('key-press-event', self.keypress)
        self.stage.set_color(Clutter.Color.new(0, 43, 54, 255)) # red,green,blue,alpha
        self.timefont = "Roboto Light 64"
        self.datefont = "Roboto Light 40"
        self.eventfont = "Roboto Light 35"
        self.staticfont = "Roboto Light 20"
        current_time = datetime.now()
        self.textcolor = Clutter.Color.new(147, 161, 161, 255) # red,green,blue,alpha
        self.eventcolor = Clutter.Color.new(42, 161, 152, 255)
        self.datecolor = Clutter.Color.new(203, 75, 22, 255)
        self.timecolor = Clutter.Color.new(38, 139, 210, 255)
        self.timetext = Clutter.Text.new_full(self.timefont, '{0:02d}:{1:02d}:{2:02d}'.format(current_time.hour, current_time.minute, current_time.second), self.timecolor)
        self.datetext = Clutter.Text.new_full(self.datefont, '{0}.{1}'.format(current_time.month, current_time.day), self.datecolor)
        self.eventtitletext = Clutter.Text.new_full(self.eventfont, '', self.eventcolor)
        self.eventtimetext = Clutter.Text.new_full(self.eventfont, '', self.textcolor)
        self.eventstatic1text = Clutter.Text.new_full(self.staticfont, 'Next event is...', self.textcolor)
        self.eventstatic2text = Clutter.Text.new_full(self.staticfont, '...in', self.textcolor)
        self.timetext.set_position(0, 0) # x,y
        self.datetext.set_position(214, 83) # x,y
        self.eventtitletext.set_position(0,140) # x,y
        self.eventtimetext.set_position(200,187) # x,y
        self.eventstatic1text.set_position(2,113) # x,y
        self.eventstatic2text.set_position(158,206) # x,y
        Clutter.Container.add_actor(self.stage, self.timetext)
        Clutter.Container.add_actor(self.stage, self.datetext)
        Clutter.Container.add_actor(self.stage, self.eventtitletext)
        Clutter.Container.add_actor(self.stage, self.eventtimetext)
        Clutter.Container.add_actor(self.stage, self.eventstatic1text)
        Clutter.Container.add_actor(self.stage, self.eventstatic2text)

        self.clock_timeline = Clutter.Timeline()
        self.clock_timeline.set_duration(1000) # timeline lasts one second
        self.clock_timeline.add_marker_at_time("one_second", 1000)
        self.clock_timeline.connect('marker-reached', self.update_time) # when marker reached, call update_time
        self.clock_timeline.set_loop(True) # update every second
        self.clock_timeline.start()

        self.pull_calendar_update()
        self.update_calendar()

        self.calendar_pull_timeline = Clutter.Timeline()
        self.calendar_pull_timeline.set_duration(3600000) # timeline lasts 1 hr
        self.calendar_pull_timeline.add_marker_at_time("one_hour", 3600000)
        self.calendar_pull_timeline.connect('marker-reached', self.pull_calendar_update)  # when marker reached, call pull_calendar_update
        self.calendar_pull_timeline.set_loop(True) # repeat the update timer
        self.calendar_pull_timeline.start()

        self.calendar_update_timeline = Clutter.Timeline()
        self.calendar_update_timeline.set_duration(60000) # timeline lasts one second
        self.calendar_update_timeline.add_marker_at_time("one_minute", 60000)
        self.calendar_update_timeline.connect('marker-reached', self.update_calendar) # when marker reached, call update_calendar
        self.calendar_update_timeline.set_loop(True) # update every minute
        self.calendar_update_timeline.start()

    def pull_calendar_update(self, timeline = None, marker_name = None, frame_num = None):
        self.xmlresponse = urlopen('###INSERT GOOGLE CALENDAR PRIVATE XML LINK HERE###')

    def update_calendar(self, timeline = None, marker_name = None, frame_num = None):
        xmltree = parse(self.xmlresponse)
        min_delta = timedelta.max
        for entry in xmltree.getroot().findall('{http://www.w3.org/2005/Atom}entry'):
            start_time = entry.find('{http://schemas.google.com/g/2005}when').attrib['startTime']
            if len(start_time) == 10:
                continue
            event_time = datetime.strptime(entry.find('{http://schemas.google.com/g/2005}when').attrib['startTime'][:-6], '%Y-%m-%dT%H:%M:%S.%f')
            event_delta = event_time - datetime.now()
            print entry.find('{http://www.w3.org/2005/Atom}title').text + ' ' + str(event_time)
            if (event_delta > timedelta(hours=0)) & (event_delta < min_delta):
                self.soonest_event = entry
                self.soonest_event_time = event_time
                self.soonest_event_name = entry.find('{http://www.w3.org/2005/Atom}title').text
                min_delta = event_delta
        self.eventtitletext.set_text(self.soonest_event_name)
        self.eventtimetext.set_text(str(min_delta)[:-10])

    def update_time(self, timeline = None, marker_name = None, frame_num = None):
        current_time = datetime.now()
        self.timetext.set_text('{0:02d}:{1:02d}:{2:02d}'.format(current_time.hour, current_time.minute, current_time.second))
        self.datetext = Clutter.Text.new_full(self.timefont, '{0}.{1}'.format(current_time.month, current_time.day), self.textcolor)

    def keypress(self, stage, event):
        if event.keyval == 120:#Clutter.keysyms.x:
            Clutter.main_quit()
            Gtk.main_quit()

class Window(Gtk.Window):

    def __init__(self):
        super(Window, self).__init__()
        self.window = Gtk.Window()  # make a new Gtk window
        self.window.set_default_size(320, 240)  # set the size
        self.window.connect('destroy', Gtk.main_quit)
        self.embed = TimeStage()  # make a new timestage
        self.window.add(self.embed)  # add the timestage to the window
        self.window.fullscreen()  # set fullscreen mode

        self.embed.show_all()  # show all the stage actors

        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON1_MOTION_MASK)

    def run(self):
        self.window.show()
        Gtk.main()


def main():
    myapp = Window()
    myapp.run()

if __name__ == "__main__":
    main()
