import os
import numpy as np
import librosa
import librosa.display
import soundfile as sf
from collections import namedtuple
import csv
# matplotlib for graph outputs
import matplotlib.pyplot as plt
import matplotlib.style as ms
ms.use('seaborn-muted')


def get_time_series(file_with_path, start_time_s=-1, end_time_s=-1):
    # method to return time series and sample rate from all or part of an audio file
    if start_time_s < 0 or end_time_s < 0:
        # load whole file
        y, sr = librosa.load(file_with_path)
    else:
        # load specific section of audio file
        # time in frames = time in seconds * sr
        f = sf.SoundFile(file_with_path)
        sr = f.samplerate
        start_time_f = int(start_time_s * sr)
        end_time_f = int(end_time_s * sr)
        data, sample_rate = sf.read(file_with_path, start=start_time_f, stop=end_time_f, dtype='float32')
        # transpose ndarray, resample, and force to mono to match librosa standards
        data_t = data.T
        data_22k = librosa.resample(data_t, sample_rate, 22050)
        y = librosa.core.to_mono(data_22k)
        sr = 22050

    TimeSeries = namedtuple('TimeSeries', ['y', 'sr'])
    output = TimeSeries(y, sr)
    return output


def extract_mfcc(file_with_path=None, y=None, sr=-1):
    # extract top 14 MFCCS for [specified part of] audio file

    if (y is None or sr < 0) and (file_with_path is not None):
        # no time series data provided; extract from whole file
        y, sr = librosa.load(file_with_path)
    else:
        print "ERROR in feature.extract_mfcc(): Invalid Arguements"
        return

    S = librosa.feature.melspectrogram(y, sr=sr, n_mels=128)
    log_S = librosa.logamplitude(S, ref_power=np.max)
    mfcc = librosa.feature.mfcc(S=log_S, n_mfcc=14)
    return mfcc


def mfcc_from_csv(file_with_path, output_dir):
    path, file_with_ext = os.path.split(file_with_path)
    path += '/'
    core, extension = os.path.splitext(file_with_ext)
    file_in_name = '%s/smcmonofeatures/%s_48kHzmfccvb.csv' % (output_dir, core)
    with open(file_in_name, 'rb') as f:
        reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        mfcc_list = list(reader)
        mfcc = np.asarray(mfcc_list)
    return mfcc


def extract_chroma(file_with_path=None, y=None, sr=-1):
    # extract chromagram for [specified part of] audio file

    if (y is None or sr < 0) and (file_with_path is not None):
        # no time series data provided; extract from whole file
        y, sr = librosa.load(file_with_path)
    else:
        print "ERROR in feature.extract_chroma(): Invalid Arguements"
        return

    S = np.abs(librosa.stft(y))
    chroma = librosa.feature.chroma_stft(S=S, sr=sr)
    return chroma


def chroma_from_csv(file_with_path, output_dir):
    path, file_with_ext = os.path.split(file_with_path)
    path += '/'
    core, extension = os.path.splitext(file_with_ext)
    file_in_name = '%s/smcmonofeatures/%s_24kHzchroma.csv' % (output_dir, core)
    with open(file_in_name, 'rb') as f:
        reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        chroma_list = list(reader)
        chroma = np.asarray(chroma_list)
    return chroma


def calc_tempo(file_with_path=None, y=None, sr=-1):
    # calculate tempo for [specified part of] audio file

    if (y is None or sr < 0) and (file_with_path is not None):
        # no time series data provided; extract from whole file
        y, sr = librosa.load(file_with_path)
    else:
        print "ERROR in feature.calc_tempo(): Invalid Arguements"
        return

    onset_env = librosa.onset.onset_strength(y, sr)
    tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
    return float(tempo)


def mfcc_to_file(mfcc, core, output_dir):
    # output mfcc to .csv file for future processing
    output_folder = "%s/smcmonofeatures/" % output_dir
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    output_file = "%s%s_48kHzmfccvb.csv" % (output_folder, core)
    np.savetxt(output_file, mfcc, delimiter=",")
    return output_file


def chroma_to_file(chroma, core, output_dir):
    # output chroma to .csv file for future processing
    output_folder = "%s/smcmonofeatures/" % output_dir
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    output_file = "%s%s_24kHzchroma.csv" % (output_folder, core)
    np.savetxt(output_file, chroma, delimiter=",")
    return output_file


def output_mfcc_image(file_with_path, mfcc, output_folder="/Volumes/AdataHD710/preprocessed/smc26khzmonoseg/"):
    # output as matplotlib file in /outputs/[core]_mfcc.png
    # handle i/o
    path, file_with_ext = os.path.split(file_with_path)
    core, extension = os.path.splitext(file_with_ext)
    output_loc = "%s%s_16khz_mono/images/" % (output_folder, core)
    if not os.path.exists(output_loc):
        os.makedirs(output_loc)

    librosa.display.specshow(mfcc)
    plt.title('MFCC - %s' % core)
    plt.ylabel('MFCC')
    plt.xlabel('Time')
    # keep tidy
    plt.tight_layout()
    plt.savefig('%s%s_mfcc.png' % (output_loc, core))
    return


def output_chroma_image(file_with_path, chroma, output_folder="/Volumes/AdataHD710/preprocessed/smc26khzmonoseg/"):
    # output as matplotlib file in /outputs/[core]_chroma.png
    # handle i/o
    path, file_with_ext = os.path.split(file_with_path)
    core, extension = os.path.splitext(file_with_ext)
    output_loc = "%s%s_16khz_mono/images/" % (output_folder, core)
    if not os.path.exists(output_loc):
        os.makedirs(output_loc)

    im = librosa.display.specshow(chroma, y_axis='chroma', x_axis='time')
    plt.title('Chromagram - %s' % core)
    # keep tidy
    plt.tight_layout()
    plt.colorbar()
    plt.savefig('%s%s_chroma.png' % (output_loc, core))
    return


def output_mel_spectogram(file_with_path,
                          y=None,
                          sr=-1,
                          output_folder="/Volumes/AdataHD710/preprocessed/smc26khzmonoseg/"):
    # output mel spectogram for all or specified part of audio file

    # handle i/o
    path, file_with_ext = os.path.split(file_with_path)
    core, extension = os.path.splitext(file_with_ext)
    output_loc = "%s%s_16khz_mono/images/" % (output_folder, core)
    if not os.path.exists(output_loc):
        os.makedirs(output_loc)

    if y is None or sr < 0:
        # no time series data provided; read whole file
        y, sr = librosa.load(file_with_path)

    duration = librosa.core.get_duration(y, sr)
    S = librosa.feature.melspectrogram(y, sr=sr, n_mels=128)
    log_S = librosa.logamplitude(S, ref_power=np.max)
    plt.figure(figsize=(12, 4))
    librosa.display.specshow(log_S, sr=sr, x_axis='time', y_axis='mel')
    plt.title('mel power spectogram')
    plt.colorbar(format='%+02.0f dB')
    plt.savefig('%s%s_melSpectogram.png' % (output_loc, core, duration))
    return
