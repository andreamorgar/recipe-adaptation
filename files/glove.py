# -*- coding: utf-8 -*-
"""
Author: Andrea Morales-Garzón

File to train a glove model, and export it to gensim format

"""

import pandas as pd 
from glove import Corpus, Glove
from gensim.models import KeyedVectors
from gensim.scripts.glove2word2vec import glove2word2vec


sst_home = '../data/'
sst_models = '../models/v2/'


df = pd.read_csv(sst_home + 'corpus_word_embedding.csv')
all_sentences_joined  = list(df['preproc cooking steps'])
all_sentences = [ str(i).split(" ") for i in all_sentences_joined]
all_sentences[:2]


# https://textminingonline.com/getting-started-with-word2vec-and-glove-in-python

#Creating a corpus object
corpus = Corpus() 

#Training the corpus to generate the co occurence matrix which is used in GloVe
corpus.fit(all_sentences, window=5)

# create Glove model object setting vector size to 300
glove = Glove(no_components=300, learning_rate=0.05) 

# train word embedding model with the corpus
glove.fit(corpus.matrix, epochs=30, no_threads=4, verbose=True)

glove.add_dictionary(corpus.dictionary)
glove.save('../models/glove.model')

# model testing: get most similar words in vocabulary given another one
glove.most_similar('lemon')

print(len(glove.word_vectors))
print(len(glove.dictionary))

# save model in a txt for future export to gensim
# data has to be saved in this specific format
with open(sst_home + 'glove.txt', 'w') as the_file:
  for i in glove.dictionary:
    v = " ".join([str(j) for j in glove.word_vectors[glove.dictionary[i]]])
    the_file.write(i + " " + v +'\n')

# https://machinelearningmastery.com/develop-word-embeddings-python-gensim/
# https://radimrehurek.com/gensim/scripts/glove2word2vec.html

# Gensim library do not able to load a GloVe model, but do allow to load the GloVe
# vectors in a gensim word2vec model format. In this way we can use the GloVe model
# with gensim utilities

# export glove vectors to a w2v gensim model
glove_input_file = sst_models + 'glove.txt'
word2vec_output_file = sst_models + 'glove.txt.word2vec'
# save the model for future use with gensim library
glove2word2vec(glove_input_file, word2vec_output_file)

filename = sst_models + 'glove.txt.word2vec'

# load the GloVe model in a word2vec structure from gensim
model = KeyedVectors.load_word2vec_format(filename, binary=False)
# testing the GloVe model with Gensim utilities
result = model.most_similar('lemon')
print(result)