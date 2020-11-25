#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 12:23:15 2019

@author: Andrea Morales Garzón

File with the word embedding model implementation using 
the Word2Vec algorithm (Mikolov, 2013).
Implementation made with the Gensim library

It also contains examples of using and preliminary tests for 
checking that the trained model works properly.

"""

# libraries

# Recipe folder
TEXT_DATA_DIR = '../recipes/'

import os
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
import gensim
from gensim.parsing.preprocessing import preprocess_string, remove_stopwords, stem_text


#%%

# w2v training

texts = []
labels_index = {} 
labels = []
label_text = []


print('Extracting recipe texts...')
for name in sorted(os.listdir(TEXT_DATA_DIR)):
    path = os.path.join(TEXT_DATA_DIR, name)
    print(name)
    if os.path.isdir(path):
        label_id = len(labels_index)
        # every directory is numbered
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

# -----------------------------------------------------------------------------


#1. Obtain tokens
print('Obtain text tokens')
tokens = [list(gensim.utils.tokenize(doc, lower=True)) for doc in texts]

#2. Bigram model training
print('Bigram model training')
bigram_mdl = gensim.models.phrases.Phrases(tokens, min_count=1, threshold=2)

# 3. Text preprocessing
CUSTOM_FILTERS = [remove_stopwords, stem_text]
tokens = [preprocess_string(" ".join(doc), CUSTOM_FILTERS) for doc in tokens]

print('Apply bigram model to recipe texts')
bigrams = bigram_mdl[tokens]
# Save bigram model
bigram_mdl.save("../models/v2/my_bigram_model.pkl")


# -----------------------------------------------------------------------------

# PARÁMETROS
    # min_count: to ignore words that appears less than 3 times
    # size: size of the word embedding vectors
    # window: window size for the context of each word
    # workers: number of proccess
    # number of epochs for training
    
all_sentences = list(bigrams)
print('Training w2v...')
model = Word2Vec(all_sentences, min_count=3, size=300, workers=4, window=5, iter=30)       

# -----------------------------------------------------------------------------

print('Guardando modelo w2v...')
model.save("../models/v2/modelo3")

# -----------------------------------------------------------------------------

#%%

# Some testing 

# https://radimrehurek.com/gensim/models/keyedvectors.html
modelo_guardado = KeyedVectors.load("../models/v2/modelo3")

# get a food word embedding representation
vector_prueba = modelo_guardado.wv['potato']

# -----------------------------------------------------------------------------
# Testing model's vocabulary....

vocab = model.wv.vocab #vocabulary
print(len(vocab)) # vocabulary size

# Find the more similar words for CAKE
modelo_guardado.wv.most_similar('cake')

# Find the more similar words for CUSTARD
modelo_guardado.wv.most_similar('custard')

# Similarity between two words
modelo_guardado.wv.similarity('biscuit','cake')
modelo_guardado.wv.similarity('pizza','lasagna')


# -----------------------------------------------------------------------------
# Some preliminary tests with the word mover's distance

sentence_1 = 'potatoes fried oil'.lower().split()

sentence_2 = 'potato, fried, oil'.lower().split()

sentence_3 = 'potato, fried, butter'.lower().split()
sentence_4 = 'potato, roasted, salt'.lower().split()

# We can apply word mover distance to get distance between food descriptions
# https://tedboy.github.io/nlps/generated/generated/gensim.models.Word2Vec.wmdistance.html 
 
similarity_1 = modelo_guardado.wv.wmdistance(sentence_1, sentence_2)
# similarity; 0.0

similarity_2 = modelo_guardado.wv.wmdistance(sentence_1, sentence_3)
# similarity; 40.613792419433594

similarity_3 = modelo_guardado.wv.wmdistance(sentence_1, sentence_4)
# similarity; 51.771560668945305



