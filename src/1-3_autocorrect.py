#!/usr/bin/env python3

# %%
# Assignment Pt. 1: Edit Distances
import numpy as np

vocabulary_file = open('../res/count_1w.txt', 'r')
lines = vocabulary_file.readlines()
vocabulary = list()
word_count = 0
# Strips the newline character
for line in lines:
    line = line.strip()
    w = line.split('\t')
    word = {'word': w[0], 'count': w[1]}
    word_count = word_count + int(w[1])
    vocabulary.append(word)

print(len(vocabulary))
print(vocabulary[0:5])


gem_doppel = [
    ("GCGTATGAGGCTAACGC", "GCTATGCGGCTATACGC"),
    ("kühler schrank", "schüler krank"),
    ("the longest", "longest day"),
    ("nicht ausgeloggt", "licht ausgenockt"),
    ("gurken schaben", "schurkengaben")
]
# %%

def hamming(s1: str, s2: str) -> int:
    distance = 0

    # pad strings to equal length
    if(len(s2) > len(s1)):
        s1 = s1.ljust(len(s2), ' ')
    else:
        s2 = s2.ljust(len(s1), ' ')

    # calculate differences in characters
    for c1, c2 in zip(s1,s2):
        if(c1 != c2):
            distance = distance + 1

    return distance

assert hamming('GCGTATGAGGCTAACGC', 'GCTATGCGGCTATACGC') == 10
assert hamming('kühler schrank', 'schüler krank') == 13
assert hamming('the longest', 'longest day') == 11
assert hamming('nicht ausgeloggt', 'licht ausgenockt') == 4
assert hamming('gurken schaben', 'schurkengaben') == 14

# %%
def levenshtein(s1: str, s2: str) -> (int, str):
    get_values = lambda v: [vv[0] for vv in v]
    operations = list()
    distances = np.zeros((len(s1)+1, len(s2)+1))

    distances[0,:] = [*range(0,len(s2)+1)]
    distances[:,0] = [*range(0,len(s1)+1)]

    
    operations.append(['i'*int(i) for i in distances[0,:]])
    for row in distances[1:,:]:
        operations.append(['d'*int(i) for i in row])
    

    for cidx in range(1,np.shape(distances)[0]):

        for ridx in range(1,np.shape(distances)[1]):

            c1 = s1[cidx-1]
            c2 = s2[ridx-1]

            deletion = (distances[cidx-1,ridx] + 1, operations[cidx-1][ridx] + 'd')
            insertion = (distances[cidx,ridx-1] + 1, operations[cidx][ridx-1] + 'i')

            if(c1 != c2):
                substitution = (distances[cidx-1,ridx-1] + 1, operations[cidx-1][ridx-1] + 's')
            else:
                substitution = (distances[cidx-1,ridx-1] + 0, operations[cidx-1][ridx-1] + 'm')

            x = [deletion, insertion, substitution]
            minimum = min(get_values(x))
            minidx = get_values(x).index(minimum)
            
            distances[cidx,ridx] = minimum
            operations[cidx][ridx] = x[minidx][1]

    distance = int(distances[-1,-1])
    operations = operations[-1][-1]

    #return (distance, operations)
    return distance

assert levenshtein('GCGTATGAGGCTAACGC', 'GCTATGCGGCTATACGC') == (3, 'mmdmmmmsmmmmmimmmm')
assert levenshtein('kühler schrank', 'schüler krank') == (6, 'ssmimmmmsddmmmm')
assert levenshtein('the longest', 'longest day') == (8, 'ddddmmmmmmmiiii')
assert levenshtein('nicht ausgeloggt', 'licht ausgenockt') == (4, 'smmmmmmmmmmsmssm')
assert levenshtein('gurken schaben', 'schurkengaben') == (7, 'siimmmmmsdddmmmm')

# %%
# Assignment Pt. 2: Auto-Correct
def suggest(w: str, dist, max_cand=5) -> list:
    """
    w: word in question
    dist: edit distance to use
    max_cand: maximum of number of suggestions

    returns a list of tuples (word, dist, score) sorted by score and distance"""
    suggestions = list()
    for word in vocabulary[:]:
        distance = dist(w, word['word'])
        Pw = int(word['count'])/word_count
        Pxw = distance
        suggestions.append((word['word'], distance, Pw))
        
    def getScore(suggestion):
        return suggestion[1]

    suggestions.sort(key=getScore)
    if (suggestions[0][1] == 0):
        return suggestions[0]
    else:
        return suggestions[:max_cand]

examples = [
    "pirates",    # in-voc
    "pirutes",    # pirates?
    "continoisly",  # continuosly?
]

for w in examples[:]:
    print(w, suggest(w, hamming, max_cand=3))

# sample result; your scores may vary!
# pirates [('pirates', 0, -11.408058827802126)]
# pirutes [('pirates', 1, -11.408058827802126), ('minutes', 2, -8.717825438953103), ('viruses', 2, -11.111468702571859)]
# continoisly [('continously', 1, -15.735337826575178), ('continuously', 2, -11.560071979871001), ('continuosly', 2, -17.009283000138204)]

# %%
# Assignment Pt. 3: Needleman-Wunsch

from bs4 import BeautifulSoup
import math 
  
# reading content
file = open("../res/de.xml", "r")
contents = file.read()
  
# parsing
soup = BeautifulSoup(contents, 'xml')
keys = soup.find_all('char')
keyboard = {}
# display content
for key in keys:
    k = {'value': key.string}
    parent = key.parent
    k['left'] = parent['left']
    k['top'] = parent['top']
    k['width'] = parent['width']
    k['height'] = parent['height']
    k['fingerIndex'] = parent['fingerIndex']
    keyboard[k['value']] = k

# space
specialKeys = soup.find_all('specialKey')
for key in specialKeys:
    if key['type'] == 'space':
        keyboard[' '] = {'left': key['left'], 'top': key['top'], 'width': key['width'], 'height': key['height']}

print(keyboard[' '])

def keyboardsim(s1: str, s2: str) -> float:
    key1 = keyboard[s1]
    key2 = keyboard[s2]
    return math.dist((int(key1['left']), int(key1['top'])), (int(key2['left']), int(key2['top'])))

def nw(s1: str, s2: str, d: float = 0, sim = keyboardsim) -> float:
    get_values = lambda v: [vv[0] for vv in v]
    operations = list()
    scores = np.zeros((len(s1)+1, len(s2)+1))

    scores[0,:] = [i*-1 for i in [*range(0,len(s2)+1)]]
    scores[:,0] = [i*-1 for i in [*range(0,len(s1)+1)]]
    
    operations.append(['-'*int(-i) for i in scores[0,:]])
    for row in scores[1:,:]:
        operations.append(['-'*int(-i) for i in row])

    for cidx in range(1,np.shape(scores)[0]):

        for ridx in range(1,np.shape(scores)[1]):

            c1 = s1[cidx-1]
            c2 = s2[ridx-1]

            deletion = (scores[cidx-1,ridx] - 1, operations[cidx-1][ridx] + '-')
            insertion = (scores[cidx,ridx-1] - 1, operations[cidx][ridx-1] + '-')

            if(c1 != c2):
                cost = sim(c1, c2)
                substitution = (scores[cidx-1,ridx-1] - cost, operations[cidx-1][ridx-1] + '-')
            else:
                substitution = (scores[cidx-1,ridx-1] + 1, operations[cidx-1][ridx-1] + '+')

            x = [deletion, insertion, substitution]
            maximum = max(get_values(x))
            minidx = get_values(x).index(maximum)
            
            scores[cidx,ridx] = maximum
            operations[cidx][ridx] = x[minidx][1]

    score = int(scores[-1,-1])
    operations = operations[-1][-1]
    
    return (score, operations)
    #return score

assert nw('GCGTATGAGGCTAACGC', 'GCTATGCGGCTATACGC', sim=lambda x,y: 1) == (12, '++-++++-+++++-++++')
assert nw('kühler schrank', 'schüler krank', sim=lambda x,y: 1) == (3, '--+-++++---++++')
assert nw('the longest', 'longest day', sim=lambda x,y: 1) == (-1, '----+++++++----')
assert nw('nicht ausgeloggt', 'licht ausgenockt', sim=lambda x,y: 1) == (8, '-++++++++++-+--+')
assert nw('gurken schaben', 'schurkengaben', sim=lambda x,y: 1) == (2, '---+++++----++++')

print(nw('GCGTATGAGGCTAACGC', 'GCTATGCGGCTATACGC'))
print(nw('kühler schrank', 'schüler krank'))
print(nw('the longest', 'longest day'))
print(nw('nicht ausgeloggt', 'licht ausgenockt'))
print(nw('gurken schaben', 'schurkengaben'))

# How does your suggest function behave with nw and a keyboard-aware similarity?

# %%
