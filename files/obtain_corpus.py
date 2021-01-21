#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 12:23:15 2019

@author: andrea
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 13:30:11 2019

@author: andrea
"""

# Import libraries to build Word2Vec model, and load Newsgroups data
import os
import sys
import re
from gensim.models import Word2Vec
from gensim.models.phrases import Phraser, Phrases
#TEXT_DATA_DIR = '/home/andrea/Escritorio/recipes_set/recipes/'
TEXT_DATA_DIR = '../recipes/'
import gensim, pprint

import numpy as np
from gensim.test.utils import get_tmpfile
from gensim.models import KeyedVectors

from gensim.parsing.preprocessing import preprocess_string, remove_stopwords, stem_text
from gensim.summarization.textcleaner import split_sentences # para tokenizar en frases independientes
import pandas as pd


#%%

# Newsgroups data is split between many files and folders.
# Directory stucture 20_newsgroup/<newsgroup label>/<post ID>
texts = []         # list of text samples
labels_index = {}  # dictionary mapping label name to numeric id
labels = []        # list of label ids
label_text = []    # list of label texts

# Go through each directory
print('Getting texts from recipe folders...')
for name in sorted(os.listdir(TEXT_DATA_DIR)):
    path = os.path.join(TEXT_DATA_DIR, name)
    print(name)
    if os.path.isdir(path):
        label_id = len(labels_index)
        # asignamos numero a cada directorio
        labels_index[name] = label_id
        for fname in sorted(os.listdir(path)):
            fpath = os.path.join(path, fname)
            f = open(fpath, encoding='latin-1')
            t = f.read()
            texts.append(t)
            f.close()
            labels.append(label_id)
            label_text.append(name)
print('Found %s texts.' % len(texts))
# >> Found 264310 texts.

#%%

# tokenize documents with gensim's tokenize() function
print('Getting tokens from the text...')
tokens = [list(gensim.utils.tokenize(doc, lower=True)) for doc in texts]

# build bigram model
print('Training bigram model...')
bigram_mdl = gensim.models.phrases.Phrases(tokens, min_count=1, threshold=2)


# Preprocessing tokens
CUSTOM_FILTERS = [remove_stopwords, stem_text]
tokens = [preprocess_string(" ".join(doc), CUSTOM_FILTERS) for doc in tokens]

# apply bigram model on tokens
print('Getting bigrams from the text...')
bigrams = bigram_mdl[tokens]

#pprint.pprint(list(bigrams))
print('Saving bigram model...')


all_sentences = list(bigrams)
print('Bigram model already saved')



#%%
all_sentences_joined = []
for i in all_sentences:
    all_sentences_joined.append(' '.join(i))
    
df = pd.DataFrame(all_sentences_joined, columns = ['preproc cooking steps'])
df['original cooking steps'] = texts
df.to_csv("../data/corpus_word_embedding.csv")
