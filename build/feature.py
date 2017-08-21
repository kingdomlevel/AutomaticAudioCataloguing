import os
import numpy as np
import librosa
import librosa.display
import soundfile as sf
from collections import namedtuple
# matplotlib for graph displays
import matplotlib.pyplot as plt
import matplotlib.style as ms
ms.use('seaborn-muted')


def output_mfcc(file_with_path, mfcc):
    # output as matplotlib file in /outputs/[core]/mfcc.png
    # handle i/o
    path, file_with_ext = os.path.split(file_with_path)
    core, extension = os.path.splitext(file_with_ext)
    output_loc = 'outputs/%s/images/' % core
    if not os.path.exists(output_loc):
        os.makedirs(output_loc)

    librosa.display.specshow(mfcc)
    plt.ylabel('MFCC')
    plt.colorbar()
    # keep tidy
    plt.tight_layout()
    plt.savefig('%s%s_%s.png' % (output_loc, core, mfcc))
    return


def extract_mfcc(file_with_path=None, y=None, sr=-1):
    # extract top 13 MFCCS for [specified part of] audio file

    if (y is None or sr < 0) and (file_with_path is not None):
        # no time series data provided; extract from whole file
        y, sr = librosa.load(file_with_path)
    else:
        print "ERROR in feature.extract_mfcc(): Invalid Arguements"
        return

    S = librosa.feature.melspectrogram(y, sr=sr, n_mels=128)
    log_S = librosa.logamplitude(S, ref_power=np.max)
    mfcc = librosa.feature.mfcc(S=log_S, n_mfcc=13)
    return mfcc


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
    print(type(tempo))
    print tempo


def output_mel_spectogram(file_with_path, y=None, sr=-1):
    # output mel spectogram for all or specified part of audio file

    # handle i/o
    path, file_with_ext = os.path.split(file_with_path)
    core, extension = os.path.splitext(file_with_ext)
    output_loc = 'outputs/%s/images/' % core
    if not os.path.exists(output_loc):
        os.makedirs(output_loc)

    if y is None or sr < 0:
        # no time series data provided; read whole file
        y, sr = librosa.load(file_with_path)

    duration = librosa.core.get_duration(y, sr)
    S = librosa.feature.melspectrogram(y, sr=sr, n_mels=128)
    log_S = librosa.logamplitude(S, ref_power=np.max)
    plt.figure(figsize=(12,4))
    librosa.display.specshow(log_S, sr=sr, x_axis='time', y_axis='mel')
    plt.title('mel power spectogram')
    plt.colorbar(format='%+02.0f dB')
    plt.savefig('%s%s_%s.png' % (output_loc, core, duration))
    return


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
