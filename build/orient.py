import pyorient
import subprocess
import sys
import os
import signal
import time


class Database:
    # class variables
    client = None
    db_name = 'BuildTest'
    pro_group = None

    def __init__(self):
        # initialise server
        shell_script = 'sh /Users/Niall/Documents/orientdb/bin/server.sh'
        # print "COMMAND:      %s" % shell_script
        shell_list = shell_script.split()
        self.pro_group = subprocess.Popen([shell_script], shell=True, stdout=subprocess.PIPE)
        # wait til orient is fully loaded before opening DB
        time.sleep(5)

    def open_db(self):
        self.client = pyorient.OrientDB('localhost', 2424)
        # connect to server
        session_id = self.client.connect('root', 'hello')

        # open database to work on
        if self.client.db_exists(self.db_name):
            self.client.db_open(self.db_name,  "admin", "admin")
            print self.db_name + " opened successfully"
        else:
            print "database [" + self.db_name + "] does not exist! session ending..."
            sys.exit()
        return

    def insert_audio_file(self, show_name, length):
        # UNFINISHED!!!!
        record = self.client.command("INSERT INTO AudioFile ()")
        # return record id for audio file (to use when creating relationships)
        return

    def insert_music_segment(self, start_time, end_time):
        record = self.client.command("INSERT INTO MusicSegment (startTime, endTime) values (%f, %f) "
                                     "RETURN @rid.asString()" % (start_time, end_time))
        record_result = record.pop()
        # get the id of the record that has just been inserted
        rid = record_result.result
        print "New MusicSegment vertex " + rid + " successfully inserted."
        return rid

    def shutdown_db(self):
        # shut down client
        self.client.shutdown('root', 'hello')
        # wait til orient is fully loaded before returning
        time.sleep(5)
        return
