import os
import sys
import subprocess
import pyorient
import time
import wave
import numpy as np
from contextlib import closing
import catalog
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

    # OPEN DB
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

    # CLOSE DB
    def shutdown_db(self):
        # shut down client
        self.client.shutdown('root', 'hello')
        # wait til orient is fully loaded before returning
        time.sleep(10)
        return

    # INSERTS
    def __insert_audio_file(self, file_with_path):
        path, file_with_ext = os.path.split(file_with_path)
        with closing(wave.open(file_with_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
        data_item = {'@AudioFile': {'Filename': file_with_ext, 'Duration': duration}}
        record = self.client.record_create(25, data_item)
        rid = record._rid
        print "New AudioFile vertex %s successfully inserted." % rid
        return rid

    def __insert_item(self, audio_file_rid, file_with_path):
        # get details from file input
        path, file_with_ext = os.path.split(file_with_path)
        path += '/'
        core, extension = os.path.splitext(file_with_ext)

        data_item = {'@Item': {'Filename': core, 'Format': extension, 'ContainingFolder': path}}
        record = self.client.record_create(69, data_item)
        rid = record._rid
        print "\tNew Item vertex %s successfully inserted." % rid
        relationship_command = "CREATE EDGE ExemplifiedBy FROM %s TO %s" % (audio_file_rid, rid)
        self.client.command(relationship_command)
        return rid

    def __insert_mfcc_representation(self, audio_file_rid, mfcc):
        mfcc_list = mfcc.tolist()
        data_item = {'@MFCC': {'Data': mfcc_list}}
        record = self.client.record_create(77, data_item)
        rid = record._rid
        print "\tNew MFCC vertex %s successfully inserted." % rid
        relationship_command = "CREATE EDGE Represents FROM %s TO %s" % (rid, audio_file_rid)
        self.client.command(relationship_command)
        return rid

    def __insert_chroma_representation(self, audio_file_rid, chroma):
        chroma_list = chroma.tolist()
        data_item = {'@Chroma': {'Data': chroma_list}}
        record = self.client.record_create(85, data_item)
        rid = record._rid
        print "\tNew Chroma vertex %s successfully inserted." % rid
        relationship_command = "CREATE EDGE Represents FROM %s TO %s" % (rid, audio_file_rid)
        self.client.command(relationship_command)
        return rid

    def __insert_catalog_item(self, audio_file_rid, file_with_path):
        # check if matching CatalogItem already exists in db (for another manifestation)
        # e.g. 2 sides of one cassette; radio recording acorss multiple cassettes; etc
        doc = catalog.generate_catalog_doc(file_with_path)
        data = json.loads(doc)
        shelf_mark = data["ShelfMark"]
        catalog_rid = self.client.query("SELECT @rid FROM CatalogItem WHERE ShelfMark = '%s'" % shelf_mark)
        if not catalog_rid:
            # need to insert new CatalogItem
            # generate catalog info from file and insert into db
            cmnd = "INSERT INTO CatalogItem CONTENT %s RETURN @rid.asString()" % doc
            # return record id for created item (to use when creating relationships)
            record = self.client.command(cmnd)
            record_result = record.pop()
            catalog_rid = record_result.result
            print "\tNew CatalogItem vertex %s successfully inserted." % catalog_rid

        # [now that] CatalogItem exists: create relationship to audio file
        audio_file_relation = "CREATE EDGE RefersTo FROM %s TO %s" % (audio_file_rid, catalog_rid)
        self.client.command(audio_file_relation)
        return catalog_rid

    def insert_music_segment(self, audio_file_rid, start_time, end_time, mfcc=None):
        if mfcc is not None:
            # create record with mfcc included
            mfcc_list = mfcc.tolist()
            data_item = {'@MusicSegment': {'MFCC': mfcc_list}}
            record = self.client.record_create(33, data_item)
        else:
            # create record without mfcc
            data_item = {'@MusicSegment': {}}
            record = self.client.record_create(33, data_item)
        # get the id of the record that has just been inserted
        rid = record._rid
        print "\t\tNew MusicSegment vertex %s successfully inserted." % rid
        relationship_command = "CREATE EDGE IsPartOf FROM %s TO %s SET startTime = %f, endTime = %f" \
                               % (rid, audio_file_rid, start_time, end_time)
        self.client.command(relationship_command)
        return rid

    def insert_speech_segment(self, audio_file_rid, start_time, end_time, label, mfcc=None):
        if mfcc is not None:
            # create record with mfcc included
            mfcc_list = mfcc.tolist()
            data_item = {'@SpeechSegment': {'Label': label, 'MFCC': mfcc_list}}
            record = self.client.record_create(37, data_item)
        else:
            # create record without mfcc
            data_item = {'@SpeechSegment': {'Label': label}}
            record = self.client.record_create(37, data_item)
        # get the id of the record that has just been inserted
        speech_rid = record._rid
        print "\t\tNew SpeechSegment vertex %s successfully inserted." % speech_rid
        relationship_to_audiofile = "CREATE EDGE IsPartOf FROM %s TO %s SET startTime = %f, endTime = %f" \
                                    % (speech_rid, audio_file_rid, start_time, end_time)
        self.client.command(relationship_to_audiofile)
        self.__add_speaker_relation(speech_rid, audio_file_rid, label)
        return speech_rid

    def __add_speaker_relation(self, speech_rid, audio_rid, label):
        # load and clean data from label for insertion / comparison purposes
        data = label.split()
        label_id = data[1].strip(',')
        sex = data[3].strip(',')
        if sex == 'M':
            sex = 'Male'
        elif sex == 'F':
            sex = 'Female'
        band = data[5]
        if band == 'S':
            band = 'Studio'
        elif band == 'T':
            band = 'Telephone'

        #   check if Person exists with Label: property matching this method's 'label' variable...
        query = "SELECT * from Person WHERE ID = '%s'" % label_id
        query_result = self.client.query(query)
        # print "QUERY RESULT:"
        # print query_result
        speaker_exists = False
        if query_result:
            # speaker with that id exists in database... but we need to check if it's related to 'this' file
            # does Person have SpokenBy relationship to a SpeechSegment where...
            speaker_id = query_result[0]._rid
            query = "SELECT in() FROM %s" % speaker_id
            query_result = self.client.query(query)
            seg_returned =  '#' + query_result[0]._in[0].get()
            # ...SpeechSegment has IsPartof relationship to AudioFile matching this method's 'audio_file_rid'?
            query = "SELECT out('IsPartOf') FROM %s" % seg_returned
            query_result = self.client.query(query)
            audio_returned = '#' + query_result[0]._out[0].get()
            if audio_returned == audio_rid:
                # speaker does exist!! no need to insert :)
                speaker_exists = True

        if not speaker_exists:
            #  need to create the new speaker in the database
            data_item = {'@Person': {'ID': label_id, 'Sex': sex, 'Band': band}}
            record = self.client.record_create(45, data_item)
            speaker_id = record._rid
            print "\t\t\tNew Speaker vertex %s successfully inserted." % speaker_id

        # create relationship from speech segment to speaker
        self.client.command("CREATE EDGE SpokenBy FROM %s TO %s" % (speech_rid, speaker_id))
        return

    def insert_sequential_relationship(self, rid_from, rid_to):
        self.client.command("CREATE EDGE FollowedBy FROM %s TO %s" % (rid_from, rid_to))
        return

    def construct_manifestation(self, file_with_path, mfcc=None, chroma=None):
        # only add to database if file is valid
        if not os.path.isfile(file_with_path):
            print "Invalid input path:\n\t" + file_with_path
            return

        # get details from file input
        path, file_with_ext = os.path.split(file_with_path)
        path += '/'
        core, extension = os.path.splitext(file_with_ext)

        # add manifestation info to database
        audio_file_rid = self.__insert_audio_file(file_with_path)
        self.__insert_catalog_item(audio_file_rid, file_with_path)
        if mfcc is not None:
            self.__insert_mfcc_representation(audio_file_rid, mfcc)
        if chroma is not None:
            self.__insert_chroma_representation(audio_file_rid, chroma)
        # include item (tho it is not the focus of the project)
        item = self.__insert_item(audio_file_rid, file_with_path)
        return audio_file_rid

    # LOADS
    def load_record(self, rid):
        # load a record with id 'rid'
        record = self.client.record_load(rid)
        return record

    def mfcc_from_database(self, mfcc_rid):
        # fetches MFCC embedded document from orient db, converts to numpy array
        record = pyorient.load_record(mfcc_rid)
        mfcc_list = record.__getattr__('MFCC')
        mfcc = np.asarray(mfcc_list)
        return mfcc

    def chroma_from_database(self, chroma_rid):
        # fetches Chroma embedded document from orient db, converts to numpy array
        record = pyorient.load_record(chroma_rid)
        chroma_list = record.__getattr__('MFCC')
        chroma = np.asarray(chroma_list)
        return chroma

    # TRUNCATE ALL VERTEXES (delete all data but maintain structure)
    def truncate_db(self):
        self.client.command("delete vertex from (select from v)")
        print "ALL VERTEXES IN DATABASE DELETED"
        return

