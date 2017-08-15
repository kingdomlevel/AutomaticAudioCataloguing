import pyorient
import subprocess
import sys
import os
import time
import catalog


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
        time.sleep(10)

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

    def insert_catalog_item(self, filename):
        doc = catalog.generate_catalog_doc(filename)
        # return record id for created item (to use when creating relationships)
        cmnd = "INSERT INTO CatalogItem CONTENT %s RETURN @rid.asString()" % doc
        record = self.client.command(cmnd)
        record_result = record.pop()
        rid = record_result.result
        print "New Item vertex %s successfully inserted." % rid
        return rid

    def insert_music_segment(self, start_time, end_time):
        record = self.client.command("INSERT INTO MusicSegment (startTime, endTime) values (%f, %f) "
                                     "RETURN @rid.asString()" % (start_time, end_time))
        record_result = record.pop()
        # get the id of the record that has just been inserted
        rid = record_result.result
        print "New MusicSegment vertex " + rid + " successfully inserted."
        return rid

    # def insert_speech_segment(self, start_time, end_time):
    #
    #
    #
    #     !~!~!~ TO DO: THIS NEXT ~!~!~!
    #
    #
    #
    #     record
    #     return rid

    def shutdown_db(self):
        # shut down client
        self.client.shutdown('root', 'hello')
        # wait til orient is fully loaded before returning
        time.sleep(10)
        return
