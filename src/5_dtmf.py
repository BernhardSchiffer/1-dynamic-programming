#!/usr/bin/env python3

# %%
import numpy as np
import librosa
import librosa.display
from librosa import stft, amplitude_to_db, fft_frequencies
import itertools

# note: librosa defaults to 22.050 Hz sample rate; adjust if needed!

# %%
dtmf_tones = [
    ('-', 0, 1000),
    ('1', 697, 1209), 
    ('2', 697, 1336), 
    ('3', 697, 1477), 
    ('A', 697, 1633),
    ('4', 770, 1209),
    ('5', 770, 1336),
    ('6', 770, 1477),
    ('B', 770, 1633),
    ('7', 852, 1209),
    ('8', 852, 1336),
    ('9', 852, 1477),
    ('C', 852, 1633),
    ('*', 941, 1209),
    ('0', 941, 1336),
    ('#', 941, 1477),
    ('D', 941, 1633)
    ]

# %%

# TODO
# 1. familiarize with librosa stft to compute powerspectrum
# 2. extract the critical bands from the power spectrum (ie. how much energy in the DTMF-related freq bins?)
# 3. define template vectors representing the state (see dtmf_tones)
# 4. for a new recording, extract critical bands and do DP do get state sequence
# 5. backtrack & collapse

# note: you will need a couple of helper functions...

def getMaxIndexInRange(values: np.ndarray, range: tuple):
    return np.argmax(values[range[0]:range[1]]) + range[0]

def findNearestIndex(arr: list, val: float):
    """returns the index of the float that is the closest to the provided value"""
    array = np.asarray(arr)
    idx = (np.abs(array - val)).argmin()
    return idx

def collapse(x: list) -> list:
    string = ''.join(ch for ch, _ in itertools.groupby(x))
    string = string.replace('-', '')
    return list(string)

assert collapse(list('44443-3-AAA')) == list('433A')

def decode(y: np.ndarray, sr: float) -> list:
    """y is input signal, sr is sample rate; returns list of DTMF-signals (no silence)"""
    S = np.abs(stft(y))
    S_db = amplitude_to_db(S)
    freqList = fft_frequencies(sr=sr)

    lowerFrequencies = [t[1] for t in dtmf_tones]
    upperFrequencies = [t[2] for t in dtmf_tones]
    lowerRange = (min(lowerFrequencies), max(lowerFrequencies))
    upperRange = (min(upperFrequencies), max(upperFrequencies))

    lowerRange = (findNearestIndex(freqList, lowerRange[0]), findNearestIndex(freqList, lowerRange[1]))
    upperRange = (findNearestIndex(freqList, upperRange[0]), findNearestIndex(freqList, upperRange[1]))

    D = np.zeros(shape=(len(dtmf_tones), len(S_db.T)), dtype=float)

    for time in range(S_db.shape[1]):
        
        lowerMax_idx = getMaxIndexInRange(S_db.T[time,:], lowerRange)
        upperMax_idx = getMaxIndexInRange(S_db.T[time,:], upperRange)

        lowerMax = freqList[lowerMax_idx]
        upperMax = freqList[upperMax_idx]

        for dtmf_idx in range(len(dtmf_tones)):
            
            dist = abs(dtmf_tones[dtmf_idx][1] - lowerMax) + abs(dtmf_tones[dtmf_idx][2] - upperMax)

            D[dtmf_idx, time] = dist

    minima = np.argmin(D, axis=0)

    tones = [dtmf_tones[m][0] for m in minima]
    print(''.join(tones))

    return collapse(tones)

# %%
import matplotlib.pyplot as plt

y, sr = librosa.load("../res/audiocheck.net_dtmf_112163_112196_11#9632_##9696.wav")
n_fft = 2048
S = np.abs(stft(y, n_fft=n_fft))
S_db = amplitude_to_db(S)

fig, ax = plt.subplots()
img = librosa.display.specshow(S_db, y_axis='log', x_axis='time', ax=ax)
ax.set_title('Power spectrogram')
fig.colorbar(img, ax=ax, format="%+2.0f dB")

result = decode(y, sr)
print(''.join(result))
assert result == list('11216311219611#9632##9696')

# %%
