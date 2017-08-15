import numpy as np
import librosa
import librosa.display

# matplotlib for displaying the output
import matplotlib.pyplot as plt
import matplotlib.style as ms
ms.use('seaborn-muted')


# method to display mel spectogram for a given audio input (probably not necessary)
def compute_mel_spectogram(audio_path):
    y, sr = librosa.load(audio_path)
    S = librosa.feature.melspectrogram(y, sr=sr, n_mels=128)
    log_S = librosa.logamplitude(S, ref_power=np.max)
    plt.figure(figsize=(12,4))
    librosa.display.specshow(log_S, sr=sr, x_axis='time', y_axis='mel')
    plt.title('mel power spectogram')
    plt.colorbar(format='%+02.0f dB')
    plt.tight_layout()
    plt.show()
    return


# def display_mfcc(file_with_path):
def display_mfcc(mfcc):
    # y, sr = librosa.load(file_with_path)
    # S = librosa.feature.melspectrogram(y, sr=sr, n_mels=128)
    # log_S = librosa.logamplitude(S, ref_power=np.max)
    # # top 13 Mel-frequency cepstral coefficients (MFCCs)
    # mfcc = librosa.feature.mfcc(S=log_S, n_mfcc=13)

    # BELOW: CODE TO DISPLAY JUST THE MFCC (no deltas)
    librosa.display.specshow(mfcc)
    plt.ylabel('MFCC')
    plt.colorbar()

    # # BELOW: CODE FOR DELTAS
    # mfcc_delta = librosa.feature.delta(mfcc)
    # mfcc_delta2 = librosa.feature.delta(mfcc, order=2)
    # # DISPLAY MSCC + FIRST 2 DELTAS
    # plt.figure(figsize=(12, 6))
    # # display mfcc
    # plt.subplot(3, 1, 1)
    # librosa.display.specshow(mfcc)
    # plt.ylabel('MFCC')
    # plt.colorbar()
    # # display first delta
    # plt.subplot(3, 1, 2)
    # librosa.display.specshow(mfcc_delta)
    # plt.ylabel('MFCC-$\Delta$')
    # plt.colorbar()
    # # display second delta
    # plt.subplot(3, 1, 3)
    # librosa.display.specshow(mfcc_delta2, sr=sr, x_axis='time')
    # plt.ylabel('MFCC-$\Delta^2$')
    # plt.colorbar()

    # keep this in
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
