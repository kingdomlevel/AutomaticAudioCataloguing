# re-write of my earlier 'lium.py' test file
import subprocess
import os
import operator


def __run_script(file_with_ext, path, core):
    jar_loc = '/Users/Niall/Documents/Uni/Project/LIUM/'
    # create a folder to place output files (keeping it tidy!)
    output_loc = 'outputs/%s/' % core
    if not os.path.exists(output_loc):
        os.makedirs(output_loc)
    output_seg = 'outputs/%s/%s.seg' % (core, core)
    # run the LIUM script using the correct input/output masks
    shell_script = ('java -Xmx2024m -jar %slium_spkdiarization-8.4.1.jar '
                    '--fInputMask=%s%s --sOutputFormat=seg --saveAllStep '
                    '--sOutputMask=%s --doCEClustering %s'
                    ) % (jar_loc, path, file_with_ext, output_seg, core)
    subprocess.call([shell_script], shell=True)
    return


def __extract_segments(core):
    # methods to return segments "as is" from LIUM scripts..
    # NOTE: speaker segments are very coarse, ie. often sequential segments of the same
    # speaker are not appended... it is recommended to tidy these segments using clean_labels()

    # handle i/o
    seg_in_name = 'outputs/%s/%s.c.seg' % (core, core)
    music_in_name = 'outputs/%s/%s.sms.seg' % (core, core)
    seg_in = open(seg_in_name, "r+")
    music_in = open(music_in_name)
    output_list = []

    # cycle thru each line in .c.seg file, append to output list
    # (for clustered speech data)
    lines = seg_in.readlines()[1:]
    for l in lines:
        # ignore cluster header lines
        if not l.startswith(';; '):
            line = l.split()
            start_time = (float(line[2])) / 100
            end_time = ((float(line[3])) / 100) + start_time
            speaker_id = 'ID: %s, Sex: %s, Band: %s' % (line[7], line[4], line[5])
            output_list.append(Seg(start_time, end_time, speaker_id))

    # cycle thru each line .sms.seg file, append to output list
    # (for music data)
    music_flag = False
    for music_line in music_in:
        music_line = music_line.strip()
        if music_line == ';; cluster j':
            # only interested in the 'music' cluster
            music_flag = True
        elif music_flag:
            # break loop at next cluster header; all music data has been read
            if music_line.startswith(';; '):
                break
            else:
                data = music_line.split()
                start_time = (float(data[2])) / 100
                end_time = ((float(data[3])) / 100) + start_time
                music_lbl = 'MUSIC'
                output_list.append(Seg(start_time, end_time, music_lbl))

    # sort output list by start time
    output_list.sort(key=operator.attrgetter('start_time'))
    seg_in.close()
    music_in.close()
    return output_list


def __clean_speakers(segments):
    # method to concatenate multiple instances of the same speaker in quick succession
    # ... basically makes a more 'coarse' edit than the initial segmentation
    input = segments
    output_list = []

    temp_seg = None
    min_time = float('inf')
    max_time = 0.0
    # # flag to specify whether the last instance of speech has been written
    # speech_output = False

    for s in segments:
        music = s.label == 'MUSIC'
        if temp_seg is None:
            # first time round the loop, or new segment after an output
            temp_seg = s
            if music:
                output_list.append(s)
                temp_seg = None
        else:
            # perform logic on speech segments to determine whether they should
            # be appended.... music segments should be outputted "as is"
            if not music:
                # speech
                time_bool = s.start_time - temp_seg.end_time <= 0.01
                same_speaker = s.label == temp_seg.label

                if same_speaker and time_bool:
                    # we should append these segments!
                    # now determie coarse seg parameters:
                    if temp_seg.start_time < min_time:
                        min_time = temp_seg.start_time
                    if s.end_time > max_time:
                        max_time = s.end_time
                    temp_seg = s
                else:
                    # found a new speaker!
                    # append (old) speech seg to output
                    if temp_seg.start_time < min_time:
                        min_time = temp_seg.start_time
                    if s.end_time > max_time:
                        max_time = s.end_time
                    output_list.append(Seg(min_time, max_time, temp_seg.label))
                    min_time = float('inf')
                    max_time = 0.0
                    temp_seg = None
            else:
                # found some music!
                # if the previous segment was speech, it still needs to be appended to output
                if temp_seg.label != 'MUSIC':
                    if temp_seg.start_time < min_time:
                        min_time = temp_seg.start_time
                    if temp_seg.end_time > max_time:
                        max_time = temp_seg.end_time
                    output_list.append(Seg(min_time, max_time, temp_seg.label))
                output_list.append(s)
                min_time = float('inf')
                max_time = 0.0
                temp_seg = None     # <--- SHOULD THIS BE '= s' ???
    return output_list


def __write_labels_to_file(core, segments):
    file_out_name = 'outputs/%s/%sAUDACITY.txt' % (core, core)
    f_out = open(file_out_name, "w")
    for s in segments:
        f_out.write("%f\t%f\t%s\n" % (s.start_time, s.end_time, s.label))
    f_out.close()
    return file_out_name


def get_audacity_labels(core):
    fine_segs = __extract_segments(core)
    coarse_segs = __clean_speakers(fine_segs)
    file_out_name = __write_labels_to_file(core, coarse_segs)
    return file_out_name


class Seg(object):
    # class variables
    start_time = 0.00
    end_time = 0.00
    label = None

    def __init__(self, start_time, end_time, label):
        self.start_time = start_time
        self.end_time = end_time
        self.label = label

    def __repr__(self):
        return "%f\t%f\t%s\n" % (self.start_time, self.end_time, self.label)
