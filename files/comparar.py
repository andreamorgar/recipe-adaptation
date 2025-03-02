# -*- coding: utf-8 -*-
"""comparar.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pIJGACY1ZH8QRcIw4xtj8pAEa4oOBM2D
"""



sst_home = '../data/'
sst_models = '../models/v2/'


from gensim.models import Word2Vec
from gensim.models import KeyedVectors
import gensim
from gensim.parsing.preprocessing import preprocess_string, remove_stopwords, stem_text
import pandas as pd
from gensim.models.phrases import Phraser

#sys.path.append(sst_file)
#os.listdir(sst_file)

from fjaccard import fjaccard_extended
from collections import Counter

df = pd.read_csv(sst_home + 'corpus_word_embedding.csv')
all_sentences_joined  = list(df['preproc cooking steps'])
all_sentences = [ str(i).split(" ") for i in all_sentences_joined]

from gensim.models import FastText

# train FastText model if need
#modelo_fasttext = FastText(all_sentences, size=300, window=5, min_count=3, workers=4)
#modelo_fasttext.save("../models/v2/model_fasttext")

# load w2v model
modelo_w2v = KeyedVectors.load(sst_models + "modelo3")

# load fastText model
modelo_ft = KeyedVectors.load(sst_models + "modelo_fasttext")

# load GloVe model
model_glove = KeyedVectors.load_word2vec_format(sst_home + 'glove.txt.word2vec', binary=False)

# load bigram model
bigram_loaded = Phraser.load(sst_models + "my_bigram_model.pkl")

# get the recipe dataset from the original source: 
# https://www.kaggle.com/shuyangli94/food-com-recipes-and-user-interactions?select=RAW_recipes.csv
df_rp= pd.read_csv(sst_home + "RAW_recipes-foodcom-kaggle.csv")

import ast
from itertools import chain

def get_literal(ing):
    return ast.literal_eval(ing)

# obtain the list of ingredient used in recipes
df_rp['ing'] = df_rp['ingredients'].apply(get_literal)
ingredients_rp = list(df_rp['ing'])


# in this way we can obtain a subset of ingredients with lengh less than 10 
# this option was not used in our final version 
y = list(set(list(list(chain(*list(ingredients_rp))))))
sublist = [i for i in y if len(i)<10]

# function to apply preprocessing to food descriptions
def preprocess_recipe(text_recipe, create_tokens = True, main_ingredient = False):
    if main_ingredient:
        pos = text_recipe.find(',')
        if pos != -1:
            text_recipe = text_recipe[0:(pos+1)]
            
    if create_tokens:
        tokens = list(gensim.utils.tokenize(text_recipe, lower=True))
        
    else:
        tokens = text_recipe
        
    tokens = preprocess_string(" ".join(tokens), [remove_stopwords, stem_text]) 
    sentenc = list(bigram_loaded[tokens])
    
    return sentenc

sublist_preprocess = [preprocess_recipe(i) for i in sublist]

# we use the Collection package for obtain a count of the ingredients in the recipe
# in this way we can extract the most usual ingredients in the recipe dataset
list_preprocess = [" ".join(preprocess_recipe(i)) for i in list(list(chain(*list(ingredients_rp))))]
count_total = Counter(list_preprocess)
df_keys = pd.DataFrame.from_dict(dict(count_total), orient='index', columns=['count'])
df_keys = df_keys.sort_values(by='count', ascending=False)
df_keys.reset_index(level=0, inplace=True)
df_keys.columns = ['ingredient','count']
#c = [len(item) for item in list_preprocess]
# sublist_1 = list(df_keys.ingredient)[:2000]
# sublist = [i for i in sublist_1 if len(i)<14]
sublist = list(df_keys.ingredient)[:1000]

# print some results 
print(df_keys.head())
print(sublist[:10])

# read the food nutrition database COFID 
df_english = pd.read_excel(sst_home + "inglesa-labeled_reducida_vegan_terminada.xlsx")
db_foods = list(df_english['Main food description'])
# we obtain their preprocessed token set to calculate similarity
db_foods_preprocessed = [preprocess_recipe(i) for i in db_foods]
db_foods_preprocessed_joined = [" ".join(preprocess_recipe(i)) for i in db_foods]
df_db_foods = pd.DataFrame(db_foods, columns = ['food'])
df_db_foods['food_preprocessed'] = db_foods_preprocessed
df_db_foods['food_preprocessed_joined'] = db_foods_preprocessed_joined

df_db_foods.head()

mapping_results = []
import numpy as np

def get_mappings(database_items,ingredient,number_instances = False, model=modelo_w2v):
    print(ingredient)
    

    # get similarity between ingredient and dataset foods
    vector_similarity = np.zeros(len(database_items))
    for i,item in enumerate(database_items):
        s = fjaccard_extended(ingredient, item, model)
        vector_similarity[i] = s

    # identify the most accurate
    sorted_list = np.argsort(vector_similarity)    
    
    if number_instances == True:
            most_similar = [ database_items[sorted_list[i]] for i in range(10) ]
            value_most_similar = [ vector_similarity[sorted_list[i]] for i in range(10) ]
            
            # inf distance value is infinity or very high, we consider there is no similar ingredient in the database
            for i,value in enumerate(value_most_similar):
                if value == np.Infinity:
                    most_similar[i] = ['No matches']
                if value > 44.0:
                    most_similar[i]  = ['No matches']
                    
    else:
        most_similar = database_items[sorted_list[0]]
        value_most_similar = vector_similarity[sorted_list[0]]    
        
        if value_most_similar == np.Infinity:
            most_similar = 'No matches'


    alternatives = [ database_items[sorted_list[i]] for i in range(10) ]
    print(alternatives)
    print(".........")

    return most_similar, value_most_similar, alternatives

"""result = []  
result_value_mapping = []

for i,element in enumerate(sublist):
    print(i)
    mapping_idiet, value_mapping, alternatives_  = get_mappings(db_foods_preprocessed,preprocess_recipe(element),number_instances=True)
    result.append(alternatives_)
    result_value_mapping.append(value_mapping)

df_results = pd.DataFrame(sublist,columns=['ingredients'])
df_results['mapping_fasttext'] = result
df_results['values_fasttext'] = result_value_mapping
df_results.to_excel(sst_home + "results_w2v_13_ene.xlsx")
"""

# obtain FastText mappings 
result = []  
result_value_mapping = []

for i,element in enumerate(sublist):
    print(i)
    mapping_idiet, value_mapping, alternatives_  = get_mappings(db_foods_preprocessed,preprocess_recipe(element),number_instances=True, model = modelo_ft)
    result.append(alternatives_)
    result_value_mapping.append(value_mapping)

df_results = pd.DataFrame(sublist,columns=['ingredients'])
df_results['mapping_fasttext'] = result
df_results['values_fasttext'] = result_value_mapping
df_results.to_excel(sst_home + "results_ft_14_ene.xlsx")

# obtain word2vec mappings 
result = []  
result_value_mapping = []

for i,element in enumerate(sublist):
    print(i)
    mapping_idiet, value_mapping, alternatives_  = get_mappings(db_foods_preprocessed,preprocess_recipe(element),number_instances=True, model = modelo_w2v)
    result.append(alternatives_)
    result_value_mapping.append(value_mapping)

df_results = pd.DataFrame(sublist,columns=['ingredients'])
df_results['mapping_w2v'] = result
df_results['values_w2v'] = result_value_mapping
df_results.to_excel(sst_home + "results_w2v_14_ene.xlsx")

# obtain GloVe mappings 
result = []  
result_value_mapping = []

for i,element in enumerate(sublist):
    print(i)
    mapping_idiet, value_mapping, alternatives_  = get_mappings(db_foods_preprocessed,preprocess_recipe(element),number_instances=True, model = model_glove)
    result.append(alternatives_)
    result_value_mapping.append(value_mapping)

df_results = pd.DataFrame(sublist,columns=['ingredients'])
df_results['mapping_glove'] = result
df_results['values_glove'] = result_value_mapping
df_results.to_excel(sst_home + "results_glove_14_ene.xlsx")