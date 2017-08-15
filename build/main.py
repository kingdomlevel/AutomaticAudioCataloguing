import os
import sys
from Tkinter import Tk
from tkFileDialog import askopenfilenames
import segment
import feature
import numpy as np
import orient
import catalog


# hide main GUI frame, but prompt file selection
# (almost definitely TEMP)
Tk().withdraw()
input_files = askopenfilenames(title='Select input file(s):')
if not input_files:
    sys.exit("No valid file(s) selected")
print input_files

db = orient.Database()
db.open_db()

for file_with_path in input_files:
    # # SEGMENTATION STUFF
    # segment.run_script(file_with_ext, path, show_name)
    # segment.get_audacity_labels(show_name)

    # # FEATURE STUFF
    # # test librosa mel spectogram display < DON'T NEED THIS
    # plot = feature.compute_mel_spectogram(filename)
    # display MFCC and first 2 deltas
    # feature.display_mfcc(filename)
    mfcc = feature.extract_mfcc(file_with_path)
    # feature.display_mfcc(mfcc)
    # print mfcc
    # mfcc_str1 = mfcc.tostring()
    # print mfcc_str1
    # mfcc_str2 = np.fromstring(mfcc_str1)
    # print mfcc_str2

    # # DATABASE STUFF
    audio_file_rid = db._insert_audio_file(file_with_path, mfcc)
    # db.insert_catalog_item(audio_file_rid, file_with_path)
    # db.insert_speech_segment(audio_file_rid, 25.5, 35.2, "TEST DATA PLEASE DELETE")
    # db.build_ontology(file_with_path)

db.shutdown_db()
