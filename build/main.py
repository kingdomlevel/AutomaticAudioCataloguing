import os
import sys
from Tkinter import Tk
from tkFileDialog import askopenfilenames
import segment
import feature
import orient


# Helper method to read segment input
def __read_segs(rid, labels):
    f_in = open(labels, "r")
    lines = f_in.readlines()
    # keep track of previous seg rid to do sequential relationships between segs
    previous_seg = None
    for l in lines:
        data = l.split()
        start_time = float(data[0])
        end_time = float(data[1])
        # # IT IS POSSIBLE TO ADD MFCCs AT THIS STAGE...
        # # below 'insert segment' methods can take mfcc ndarray as a parameter...
        # # TO DO: figure out if this is worth doing... e.g.
        # time_series = feature.get_time_series(file_with_path, start_time, end_time)
        # seg_mfcc = feature.extract_mfcc(file_with_path, time_series.y, time_series.sr)
        if data[2] == 'MUSIC':
            # add music segments
            seg_rid = db.insert_music_segment(rid, start_time, end_time)
            # db.insert_music_segment(rid, start_time, end_time, seg_mfcc)
        else:
            # add speaker segments
            speaker_lbl = "%s %s %s %s %s %s" % (data[2], data[3], data[4], data[5], data[6], data[7])
            seg_rid = db.insert_speech_segment(rid, start_time, end_time, speaker_lbl)
            # db.insert_speech_segment(rid, start_time, end_time, speaker_lbl, seg_mfcc)
        # generate sequential relationship between segments
        if previous_seg is None:
            previous_seg = seg_rid
        else:
            db.insert_sequential_relationship(previous_seg, seg_rid)
            previous_seg = seg_rid
    f_in.close()


# hide main GUI frame, but prompt file selection
# (almost definitely TEMP)
Tk().withdraw()
input_files = askopenfilenames(title='Select input file(s):')
if not input_files:
    sys.exit("No valid file(s) selected")
print input_files

# db = orient.Database()
# db.open_db()

for file_with_path in input_files:
    # get details from file input
    path, file_with_ext = os.path.split(file_with_path)
    path += '/'
    core, extension = os.path.splitext(file_with_ext)

    if (extension.lower() == ".wav") or (extension.lower() == ".mp3"):
        # assuming LIUM segmentationhas been completed either on HPCCs or via 'preprocess.py'

        # generate audacity label file
        # output_dir = "/Users/Niall/Desktop/evaluation"    # default value
        # label_file = segment.get_audacity_labels(core, output_dir)

        # assuming mfcc / chroma has already been generated either on HPCCs or via 'preprocess.py'
        # get representations from file

        # time_series = feature.get_time_series(file_with_path)
        # y = time_series.y
        # sr = time_series.sr

        mfcc = feature.mfcc_from_csv(file_with_path)
        # chroma = feature.chroma_from_csv(file_with_path, output_dir)

        # feature.output_mfcc_image(file_with_path, mfcc)
        # feature.output_chroma_image(file_with_path, chroma)
        # feature.output_mel_spectogram(file_with_path)

        # CONSTRUCT ONTOLOGY:
        # mainifestation layer
        # audio_file_rid = db.construct_manifestation(file_with_path, mfcc, chroma)   # mfcc and chroma are optional
        # read segmentation label file to construct sub-manifestation layer
        # __read_segs(audio_file_rid, label_file)

        # insert item (though it is not primary focus of the project)
        # db.insert_item(audio_file_rid, file_with_path)

    else:
        print "File %s is not valid audio input; please select .wav or .mp3" % file_with_ext

# db.shutdown_db()
