# python file with the purpose of performing "pre-processing"
# ... that is, the same processes that have been performed on HPCC for the provided data
# explicitly, creates segmentation files using 'segment.py', and extracts MFCC and chroma features using 'feature.py'

import feature
import segment
from Tkinter import Tk
from tkFileDialog import askopenfilenames
import sys
import os

# prompt file input (single or multiple)
Tk().withdraw()
input_files = askopenfilenames(title='Select file(s) to perform processing on:')
if not input_files:
    sys.exit("No valid file(s) selected")

# loop in case of multiple files
for file_with_path in input_files:
    # get details from file input
    path, file_with_ext = os.path.split(file_with_path)
    path += '/'
    core, extension = os.path.splitext(file_with_ext)

    if (extension == ".wav") or (extension == ".mp3"):
        # run segmentation
        segment.run_script(file_with_path)

        # extract features
        mfcc = feature.extract_mfcc(file_with_path)
        chroma = feature.extract_chroma(file_with_path)
        # save features to .csv files
        feature.mfcc_to_file(mfcc, core)
        feature.chroma_to_file(chroma, core)
    else:
        print "File %s is not valid audio input; please select .wav or .mp3" % file_with_ext
