import feature
import segment
import orient
import os
import shutil


class Control:
    # class variables
    output_folder = ""
    db = None
    labels = ""

    def __init__(self, output_location):
        global output_folder
        global db
        output_folder = output_location
        db = orient.Database()
        db.open_db()

    def set_output_folder(self, output_dir):
        global output_folder
        output_folder = output_dir

    @staticmethod
    def preprocess_input(input_files, output_loc):
        # method to perform pre-processing on specified input
        # ... that is, the same processes that have been performed on HPCC for the provided data
        # explicitly, segment using 'segment.py'; extract MFCC & chroma features using 'feature.py'

        # string for output
        output = "  Pre-processing:\n"
        # header ljne
        output += "{:48}{:8}{:8}{:8}\n{:-<72}\n".format("FILE", "SEGMENT", "  MFCC", "CHROMA", "")
        for file_with_path in input_files:
            # get details from file input
            path, file_with_ext = os.path.split(file_with_path)
            path += '/'
            core, extension = os.path.splitext(file_with_ext)

            if (extension == ".wav") or (extension == ".mp3"):
                # valid input: (pre)process file

                # run segmentation - NO SPACES ALLOWED for lium script
                # create copy of file (in same directory) and replace spaces w/ undersccores
                if ' ' in file_with_path:
                    new_file_with_path = file_with_path.replace(' ', '_')
                    shutil.copy(file_with_path, new_file_with_path)
                    file_with_path = new_file_with_path
                segment.run_script(file_with_path, output_loc)
                # check for success; relay for output
                wanted_output = "%s/smc26khzmonoseg/%s_16khz_mono/%s_16khz_mono.txt" % (output_loc, core, core)
                if os.path.exists(wanted_output) and os.path.isfile(wanted_output):
                    seg_ok = " OK"
                else:
                    seg_ok = " Fail"

                # extract features
                try:
                    mfcc = feature.extract_mfcc(file_with_path)
                    chroma = feature.extract_chroma(file_with_path)
                    # save features to .csv files
                    feature.mfcc_to_file(mfcc, core, output_loc)
                    feature.chroma_to_file(chroma, core, output_loc)
                    feature_ok_bool = True
                except:
                    feature_ok_bool = False
                if feature_ok_bool:
                    feature_ok = " OK"
                else:
                    feature_ok = " Fail"
                output += "{:48}{:8}{:8}{:8}\n".format(file_with_ext, seg_ok, feature_ok, feature_ok)
            else:
                # invalid input
                output += "{:48}{:24}\n".format(file_with_ext, "! ! INVALID FORMAT ! !")
        return output

    def process_files(self, input_files, output_loc):
        global db
        output = "  Adding files to database...\n"

        for file_with_path in input_files:
            # get details from file input
            path, file_with_ext = os.path.split(file_with_path)
            path += '/'
            core, extension = os.path.splitext(file_with_ext)

            # header ljne
            output += "File: {:72}\n".format(file_with_ext)

            if (extension == ".wav") or (extension == ".mp3"):
                # valid input: now check for pre-processing!
                seg_txt = "%s/smc26khzmonoseg/%s_16khz_mono/%s_16khz_mono.txt" % (output_loc, core, core)
                mfcc_file = "%s/smcmonofeatures/%s_48kHzmfccvb.csv" % (output_folder, core)
                chroma_file = "%s/smcmonofeatures/%s_24kHzchroma.csv" % (output_folder, core)
                segmented = os.path.exists(seg_txt) and os.path.isfile(seg_txt)
                mfcc_bool = os.path.exists(mfcc_file) and os.path.isfile(mfcc_file)
                chroma_bool = os.path.exists(chroma_file) and os.path.isfile(chroma_file)

                # get data about file based on pre-procressing results
                if segmented:
                    label_file = segment.get_audacity_labels(core, output_loc)
                else:
                    output += "\tNo segmentation data found!\n\t\tCheck output folder; validate pre-processing...\n"
                    segs_txt = ""
                if mfcc_bool:
                    mfcc = feature.mfcc_from_csv(file_with_path, output_loc)
                    mfcc_txt = "\t\tMFCC data,\n"
                else:
                    mfcc = None
                    mfcc_txt = ""
                if chroma_bool:
                    chroma = feature.chroma_from_csv(file_with_path, output_loc)
                    chroma_txt = "\t\tChroma Data,\n"
                else:
                    chroma = None
                    chroma_txt = ""

                # CONSTRUCT ONTOLOGY:
                # mainifestation layer
                audio_file_rid = db.construct_manifestation(file_with_path, mfcc, chroma)  # mfcc & chroma are optional
                aud_txt = "\tAudioFile %s;\n" % audio_file_rid
                catalog_txt = "\t\tCatalogItem,\n"

                # sub-manifestatins (segments) if segmentation file exists
                if segmented:
                    self.__read_segs(audio_file_rid, label_file)
                    segs_txt = "\t\tMusic/Speech segments,\n"

                # insert item (though it is not primary focus of the project)
                db.insert_item(audio_file_rid, file_with_path)
                item_txt = "\t\tItem."

                # relay to output
                output += "\tThe following vertexes have been created:\n" \
                          "%s%s%s%s%s%s\n" % (aud_txt, catalog_txt, segs_txt, chroma_txt, mfcc_txt, item_txt)
                # footer line
                output += "{:-<72}\n\n".format("")

            else:
                # invalid input
                output += "{:72}\n{:-<72}\n\n".format("! INVALID FORMAT !", "")

        return output

    @staticmethod
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

    @staticmethod
    def truncate_database():
        global db
        output_txt = db.truncate_db()
        return output_txt

    @staticmethod
    def shutdown_db():
        global db
        db.shutdown_db()
