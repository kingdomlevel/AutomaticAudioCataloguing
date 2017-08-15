import pyorient
import subprocess
import sys
from contextlib import closing
import time
import catalog
import wave
import os


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
            print "FATAL: Database " + self.db_name + " cannot be found!"
            sys.exit()
        return

    def insert_audio_file(self, file_with_path):
        path, file_with_ext = os.path.split(file_with_path)
        with closing(wave.open(file_with_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
        record = self.client.command("INSERT INTO AudioFile (Filename, Duration) values ('%s', %f) "
                                     "RETURN @rid.asString()" % (file_with_ext, duration))
        print "INSERT INTO AudioFile (Filename, Duration) values ('%s', %f) RETURN @rid.asString()"\
              % (file_with_ext, duration)
        # get the id of the record that has just been inserted
        record_result = record.pop()
        rid = record_result.result
        print "New AudioFile vertex %s successfully inserted." % rid
        return rid

    def insert_catalog_item(self, audio_file_rid, file_with_path):
        # generate catalog info from file
        doc = catalog.generate_catalog_doc(file_with_path)
        # insert catalog item from
        cmnd = "INSERT INTO CatalogItem CONTENT %s RETURN @rid.asString()" % doc
        # return record id for created item (to use when creating relationships)
        record = self.client.command(cmnd)
        record_result = record.pop()
        rid = record_result.result
        # create relationship to audio file
        relationship_command = "CREATE EDGE RefersTo FROM %s TO %s" % (audio_file_rid, rid)
        self.client.command(relationship_command)
        print "New Item vertex %s successfully inserted." % rid
        return rid

    def insert_music_segment(self, start_time, end_time):
        # DO THIS SOON!!!
        # NEEDS FIXED: INSTEAD, GOING TO STORE START / END TIME ON THE RELATIONSHIP
        record = self.client.command("INSERT INTO MusicSegment (startTime, endTime) values (%f, %f) "
                                     "RETURN @rid.asString()" % (start_time, end_time))
        record_result = record.pop()
        # get the id of the record that has just been inserted
        rid = record_result.result
        print "New MusicSegment vertex " + rid + " successfully inserted."
        return rid

    def insert_speech_segment(self, label):
        record = self.client.command("INSERT INTO SpeechSegment (Label) values (%s) "
                                     "RETURN @rid.asString()" % label)
        record_result = record.pop()
        # get the id of the record that has just been inserted
        rid = record_result.result
        print "New SpeechSegment vertex %s successfully inserted." % rid
        return rid

    def shutdown_db(self):
        # shut down client
        self.client.shutdown('root', 'hello')
        # wait til orient is fully loaded before returning
        time.sleep(10)
        return
