import pyorient
import subprocess
import sys
from contextlib import closing
import time
import catalog
import feature
import wave
import os
import numpy as np
import json


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

    def _insert_audio_file(self, file_with_path, mfcc):
        # TO DO: consider including MFCC?
        path, file_with_ext = os.path.split(file_with_path)
        with closing(wave.open(file_with_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
        record = self.client.command("INSERT INTO AudioFile (Filename, Duration) values ('%s', %f) "
                                     "RETURN @rid.asString()" % (file_with_ext, duration))
        # get the id of the record that has just been inserted
        record_result = record.pop()
        rid = record_result.result
        mfcc = feature.extract_mfcc(file_with_path)
        data = mfcc.tobytes()
        self.client.record_update()
        print "New AudioFile vertex %s successfully inserted." % rid
        return rid

    def __insert_catalog_item(self, audio_file_rid, file_with_path):
        # generate catalog info from file
        doc = catalog.generate_catalog_doc(file_with_path)
        # insert catalog item from
        cmnd = "INSERT INTO CatalogItem CONTENT %s RETURN @rid.asString()" % doc
        # return record id for created item (to use when creating relationships)
        record = self.client.command(cmnd)
        record_result = record.pop()
        rid = record_result.result
        print "New CatalogItem vertex %s successfully inserted." % rid
        # create relationship to audio file
        relationship_command = "CREATE EDGE RefersTo FROM %s TO %s" % (audio_file_rid, rid)
        self.client.command(relationship_command)
        return rid

    def __insert_music_segment(self, audio_file_rid, start_time, end_time):
        # DO THIS SOON!!!
        # NEEDS FIXED: INSTEAD, GOING TO STORE START / END TIME ON THE RELATIONSHIP
        record = self.client.command("INSERT INTO MusicSegment (startTime, endTime) values (%f, %f) "
                                     "RETURN @rid.asString()" % (start_time, end_time))
        record_result = record.pop()
        # get the id of the record that has just been inserted
        rid = record_result.result
        print "New MusicSegment vertex %s successfully inserted." % rid
        relationship_command = "CREATE EDGE IsPartOf FROM %s TO %s SET startTime = %f, endTime = %f" \
                               % (rid, audio_file_rid, start_time, end_time)
        self.client.command(relationship_command)
        return rid

    def __insert_speech_segment(self, audio_file_rid, start_time, end_time, label):
        record = self.client.command("INSERT INTO SpeechSegment (Label) values ('%s') "
                                     "RETURN @rid.asString()" % label)
        record_result = record.pop()
        # get the id of the record that has just been inserted
        rid = record_result.result
        print "New SpeechSegment vertex %s successfully inserted." % rid
        relationship_command = "CREATE EDGE IsPartOf FROM %s TO %s SET startTime = %f, endTime = %f"\
                               % (rid, audio_file_rid, start_time, end_time)
        self.client.command(relationship_command)
        return rid

    def build_ontology(self, file_with_path):
        if not os.path.isfile(file_with_path):
            print "Invalid input path:\n\t" + file_with_path
            return

        # get details from file input
        path, file_with_ext = os.path.split(file_with_path)
        path += '/'
        core, extension = os.path.splitext(file_with_ext)

        # add manifestation info to database
        audio_file_rid = self._insert_audio_file(file_with_path)
        self.__insert_catalog_item(audio_file_rid, file_with_path)

        # read segmentation label file to construct sub-manifestation layer of ontology
        file_in_name = 'outputs/%s/%sAUDACITY.txt' % (core, core)
        f_in = open(file_in_name, "r")
        lines = f_in.readlines()
        for l in lines:
            data = l.split()
            print data
            if data[2] == 'MUSIC':
                # add music segments
                self.__insert_music_segment(audio_file_rid, float(data[0]), float(data[1]))
            else:
                # add speaker segments
                speaker_lbl = "%s %s %s %s %s %s" % (data[2], data[3], data[4], data[5], data[6], data[7])
                self.__insert_speech_segment(audio_file_rid, float(data[0]), float(data[1]), speaker_lbl)

        f_in.close()
        return

    def shutdown_db(self):
        # shut down client
        self.client.shutdown('root', 'hello')
        # wait til orient is fully loaded before returning
        time.sleep(10)
        return
