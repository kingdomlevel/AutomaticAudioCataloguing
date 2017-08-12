# re-write of my earlier 'lium.py' test file
import subprocess
import os


def run_script(file_with_ext, path, core):
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


def get_audacity_labels(core):
    # handle i/o
    seg_in_name = 'outputs/%s/%s.c.seg' % (core, core)
    music_in_name = 'outputs/%s/%s.sms.seg' % (core, core)
    file_out_name = 'outputs/%s/%sAUDACITY.txt' % (core, core)
    seg_in = open(seg_in_name, "r+")
    music_in = open(music_in_name)
    f_out = open(file_out_name, "w")

    # cycle thru each line in .c.seg file, write info to audacity labels
    # (for clustered speech data)
    lines = seg_in.readlines()[1:]
    for l in lines:
        line = l.split()
        start_time = (float(line[2])) / 100
        end_time = ((float(line[3])) / 100) + start_time
        speaker_id = 'ID: %s, Sex: %s, Band: %s, ' % (line[7], line[4], line[5])
        f_out.write("%f\t%f\t%s\n" % (start_time, end_time, speaker_id))

    # cycle thru each line .sms.seg file, write info to audacity labels
    # (for music data)
    flag = False
    for music_line in music_in:
        music_line = music_line.strip()
        if music_line == ';; cluster j':
            flag = True
        elif flag:
            if music_line.startswith(';; '):
                break
            else:
                # do summit here
                data = music_line.split()
                start_time = (float(data[2])) / 100
                end_time = ((float(data[3])) / 100) + start_time
                music_lbl = 'MUSIC'
                f_out.write("%f\t%f\t%s\n" % (start_time, end_time, music_lbl))
                # end

    # close i/o
    seg_in.close()
    f_out.close()
    return
