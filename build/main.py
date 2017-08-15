import os
import sys
from Tkinter import Tk
from tkFileDialog import askopenfilename
import segment
import feature
import numpy
import orient
import catalog


# hide main GUI frame, but prompt file selection
# (almost definitely TEMP)
Tk().withdraw()
file_with_path = askopenfilename()
# can prob get rid of this 'if' statement once we know how file input is gonna get done
if os.path.isfile(file_with_path):
    path, file_with_ext = os.path.split(file_with_path)
    path += '/'
    show_name, extension = os.path.splitext(file_with_ext)
else:
    # invalid input path: exit system
    sys.exit("Invalid input path: must be valid path to file")


# run LIUM scripts to get seg outputs and audacity labels
# segment.run_script(file_with_ext, path, show_name)
segment.get_audacity_labels(show_name)

# test librosa mel spectogram display < DON'T NEED THIS
# plot = feature.compute_mel_spectogram(filename)
# display MFCC and first 2 deltas
# feature.display_mfcc(filename)
# mfcc = feature.extract_mfcc(filename)
# print(mfcc)

# database stuff
db = orient.Database()
db.open_db()
audio_file = db.insert_audio_file(file_with_path)
db.insert_catalog_item(audio_file, file_with_path)
db.shutdown_db()
