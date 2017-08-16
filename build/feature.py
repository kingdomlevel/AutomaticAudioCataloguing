import numpy as np
import librosa
import librosa.display
import pyorient
import soundfile as sf
# matplotlib for graph displays
import matplotlib.pyplot as plt
import matplotlib.style as ms
ms.use('seaborn-muted')


def display_mfcc(mfcc):
    # display as matplotlib plot
    librosa.display.specshow(mfcc)
    plt.ylabel('MFCC')
    plt.colorbar()
    # keep tidy
    plt.tight_layout()
    plt.show()
    return


def extract_mfcc(file_with_path):
    y, sr = librosa.load(file_with_path)
    S = librosa.feature.melspectrogram(y, sr=sr, n_mels=128)
    log_S = librosa.logamplitude(S, ref_power=np.max)
    # top 13 Mel-frequency cepstral coefficients (MFCCs)
    mfcc = librosa.feature.mfcc(S=log_S, n_mfcc=13)
    return mfcc


def mfcc_from_database(rid):
    record = pyorient.load_record(rid)
    mfcc_list = record.__getattr__('MFCC')
    mfcc = np.asarray(mfcc_list)
    return mfcc


def calc_tempo(file_with_path):
    y, sr = librosa.load(file_with_path)
    onset_env = librosa.onset.onset_strength(y, sr)
    tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
    print(type(tempo))
    print tempo


def display_mel_spectogram(file_with_path):
    # probs won't need this
    y, sr = librosa.load(file_with_path)
    S = librosa.feature.melspectrogram(y, sr=sr, n_mels=128)
    log_S = librosa.logamplitude(S, ref_power=np.max)
    plt.figure(figsize=(12,4))
    librosa.display.specshow(log_S, sr=sr, x_axis='time', y_axis='mel')
    plt.title('mel power spectogram')
    plt.colorbar(format='%+02.0f dB')
    plt.tight_layout()
    plt.show()
    return
