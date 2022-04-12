#!/usr/bin/env python3

# %%
import numpy as np
import librosa
from librosa.feature import mfcc
import os

# TODO: read in files, compute MFCC, organize

def loadSpeaker(speakerName: str, index: int, base_path =  "../res/recordings/"):    
    mfccs = []
    for digitLabel in range(0, 10):
        path = os.path.join(base_path, f'{digitLabel}_{speakerName}_{index}.wav')
        print(path)
        signal, sr = librosa.load(path)
        mfccs.append({"example": f'{speakerName}_{digitLabel}', "observation": mfcc(y=signal, sr=sr).T})   
    return mfccs

jackson1 = loadSpeaker(speakerName='jackson', index=1)
jackson10 = loadSpeaker(speakerName='jackson', index=10)
george = loadSpeaker(speakerName='george', index=1)

# %%
def dtw(obs1: list, obs2: list, sim) -> float:

    l1, l2 = len(obs1), len(obs2)
    D = np.full(shape=(l1 +1, l2 +1), fill_value=np.inf, dtype=float)
    D[0,0] = 0

    for i in range (1, l1 +1):
        for j in range (1, l2 + 1):
            cost = sim(obs1[i-1], obs2[j-1])
            D[i,j] = cost + min(D[i-1,j], D[i,j-1], D[i-1,j-1])

    return D[l1, l2]

# %% [markdown]
"""
# Experiment 1

Compute DTW scores between different digits and speakers.
How do scores change across speakers and across digits?
""" 

# %%
def recognize(obs: list, refs: dict) -> str:
    """
    obs: input observations (mfcc)
    refs: dict of (classname, observations) as references
    returns classname where distance of observations is minumum
    """
    scores = []
    for sample in refs:
        score = dtw(obs, sample["observation"], lambda x,y: np.linalg.norm(x-y, ord=1))
        scores.append({"example": sample["example"], "score": score })

    return min(scores, key= lambda t: t["score"])["example"]

# %% [markdown]
"""
# Experiment 2: speaker-dependent IWR

From the same speaker, pick training and test recordings
"""
for i in range(10):
    print(f'{i}: recognize -> {recognize(jackson10[i]["observation"], jackson1)}')

# %% [markdown]
"""
# Experiment 3: speaker-independent IWR

Select training/reference set from one speaker, test recordings from the other. 
Can you compute Prec/Recall/F1?
"""

for i in range(10):
    print(f'{i}: recognize -> {recognize(jackson10[i]["observation"], george)}')

# %%
