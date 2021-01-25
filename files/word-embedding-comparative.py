#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 12:23:15 2019

@author: Andrea Morales Garzón

File with the word embedding model implementation using 
the fastText algorithm.
Implementation made with the Gensim library

It also contains examples of using and preliminary tests for 
checking that the trained model works properly.

"""

# libraries

# Recipe folder
TEXT_DATA_DIR = '../recipes/'


from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from fjaccard import fjaccard_extended
import gensim
from gensim.parsing.preprocessing import preprocess_string, remove_stopwords, stem_text
import pandas as pd
from gensim.models.phrases import Phraser
#%%

df = pd.read_csv('../data/corpus_word_embedding.csv')
all_sentences_joined  = list(df['preproc cooking steps'])
all_sentences = [ str(i).split(" ") for i in all_sentences_joined]
#%%
from gensim.models import FastText
#modelo_fasttext = FastText(all_sentences, size=300, window=5, min_count=3, workers=4)



#modelo_fasttext = FastText(all_sentences,size=100, window=5, min_count=5, workers=4, sg=0)
#%%
#modelo_fasttext.save("../models/v2/model_fasttext")

modelo_w2v = KeyedVectors.load("../models/v2/modelo3")
modelo_ft = KeyedVectors.load("../models/v2/modelo_fasttext")

modelo_ft.wv.most_similar('cake')
#%%

bigram_loaded = Phraser.load("../models/v2/my_bigram_model.pkl")
# vaoms a obtener la lista de ingredientes en las recetas
df_rp= pd.read_csv("../data/RAW_recipes-foodcom-kaggle.csv")

#%%

import ast

def get_literal(ing):
    return ast.literal_eval(ing)

df_rp['ing'] = df_rp['ingredients'].apply(get_literal)

ingredients_rp = list(df_rp['ing'])


from itertools import chain

y = list(set(list(list(chain(*list(ingredients_rp))))))





# we get a random sample



#%%
# obtain mappings

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

#%%
# sublist forma 1: nos quedamos con los mas simples
    
sublist = [i for i in y if len(i)<10]
sublist_preprocess = [preprocess_recipe(i) for i in sublist]


#%%
from collections import Counter
list_preprocess = [" ".join(preprocess_recipe(i)) for i in list(list(chain(*list(ingredients_rp))))]
count_total = Counter(list_preprocess)
df_keys = pd.DataFrame.from_dict(dict(count_total), orient='index', columns=['count'])
df_keys = df_keys.sort_values(by='count', ascending=False)
df_keys.reset_index(level=0, inplace=True)
df_keys.columns = ['ingredient','count']
#c = [len(item) for item in list_preprocess]
sublist_1 = list(df_keys.ingredient)[:2000]
sublist = [i for i in sublist_1 if len(i)<14]
#d = {item:c.count(item) for item in list_preprocess}
#
#
#repeticiones = {}
#for i in list_preprocess:
#    if i in list(repeticiones.keys()):
#        repeticiones[i] += 1
#    else:
#        repeticiones[i] = 1
#        
#df_keys = pd.DataFrame.from_dict(repeticiones, orient='index', columns=['count'])
#df_keys.reset_index(level=0, inplace=True)
#
#df_keys = df_keys.sort_values(by='count', ascending=False)




#%%

df_english = pd.read_excel("../data/inglesa-labeled_reducida_vegan_terminada.xlsx")
db_foods = list(df_english['Main food description'])
db_foods_preprocessed = [preprocess_recipe(i) for i in db_foods]
db_foods_preprocessed_joined = [" ".join(preprocess_recipe(i)) for i in db_foods]

df_db_foods = pd.DataFrame(db_foods, columns = ['food'])
df_db_foods['food_preprocessed'] = db_foods_preprocessed
df_db_foods['food_preprocessed_joined'] = db_foods_preprocessed_joined
#%%
mapping_results = []
import numpy as np

def get_mappings(database_items,ingredient,number_instances = False):
    print(ingredient)
    

    # get similarity between ingredient and dataset foods
    vector_similarity = np.zeros(len(database_items))
    for i,item in enumerate(database_items):
        s = fjaccard_extended(ingredient, item ,modelo_w2v)
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
        print("entra")
        most_similar = database_items[sorted_list[0]]
        value_most_similar = vector_similarity[sorted_list[0]]    
        
        if value_most_similar == np.Infinity:
            most_similar = 'No matches'


    alternatives = [ database_items[sorted_list[i]] for i in range(10) ]
    print(alternatives)
    print(".........")

    return most_similar, value_most_similar, alternatives
    

#%%   
result = []  
result_value_mapping = []

for i,element in enumerate(sublist):
    print(i)
    mapping_idiet, value_mapping, alternatives_  = get_mappings(db_foods_preprocessed,preprocess_recipe(element),number_instances=True)

#    mapping = df_db_foods[df_db_foods['food_preprocessed_joined'] == " ".join(mapping_idiet)]
    
    result.append(alternatives_)
    result_value_mapping.append(value_mapping)
    
#    if len(mapping) > 0:
#        print(mapping.iloc[0]['food'])
#        result.append(mapping.iloc[0]['food'])
#    else:
#        print('No matches')
#        result.append('No matches')
    
df_results = pd.DataFrame(sublist[:23],columns=['ingredients'])
df_results['mapping_w2v'] = result
df_results['values_w2v'] = result_value_mapping
df_results.to_excel("results_fasttext.xlsx")
   
#%%
result = []  
for i,element in enumerate(sublist):
    
    mapping_idiet, value_mapping, alternatives_  = get_mappings(db_foods_preprocessed,preprocess_recipe(element),number_instances=True)
    mapping = df_db_foods[df_db_foods['food_preprocessed_joined'] == " ".join(mapping_idiet)]
    

    
    if len(mapping) > 0:
        print(mapping.iloc[0]['food'])
        result.append(mapping.iloc[0]['food'])
    else:
        print('No matches')
        result.append('No matches')
        
        
#%%        
        
#get_mappings(db_foods_preprocessed,preprocess_recipe("Creme Cheese"))
        
df_results = pd.DataFrame(sublist,columns=['ingredients'])
df_results['mapping_w2v'] = result
df_results['values_w2v'] = result_value_mapping
df_results.to_excel("results_w2v.xlsx")






#%%
def get_first(element):
    return " ".join(ast.literal_eval(element)[0])

def get_third(element):
    res = ast.literal_eval(element)[0:3]
    
    res = [" ".join(i) for i in res]
    print(res)
    return res

    
def get_first_value(element):
    if 'inf' in element:
        return 1
    else:
        return ast.literal_eval(element)[0]


# load results with each word embedding model
df_mapping_w2v = pd.read_excel("results_ft_13_ene.xlsx")
df_mapping_w2v = df_mapping_w2v.set_index('ingredients')

df_mapping_ft = pd.read_excel("results_w2v_13_ene.xlsx")
df_mapping_ft = df_mapping_ft.set_index('ingredients')

df_mapping_glove = pd.read_excel("results_glove_13_ene.xlsx")
df_mapping_glove = df_mapping_glove.set_index('ingredients')


# we concat the result to work with one unique dataframe
result = pd.concat([df_mapping_w2v, df_mapping_ft, df_mapping_glove], axis=1, join="inner")

# dataframe preprocessing
result['best_w2v'] = result.mapping_w2v.apply(get_first)
result['best3_w2v'] = result.mapping_w2v.apply(get_third)
result['best_w2v_value'] = result.values_w2v.apply(get_first_value)

result['best_ft'] = result.mapping_fasttext.apply(get_first)
result['best3_ft'] = result.mapping_fasttext.apply(get_third)
result['best_ft_value'] = result.values_fasttext.apply(get_first_value)

result['best_glove'] = result.mapping_glove.apply(get_first)
result['best3_glove'] = result.mapping_glove.apply(get_third)
result['best_glove_value'] = result.values_glove.apply(get_first_value)


#%%


result = result[(result['best_w2v_value'] != 1) & (result['best_ft_value'] != 1) ]
result.quantile(0.75)
#result = result[(result['best_w2v_value'] <0.48) & (result['best_ft_value'] <0.481) ]
#result = result[(result['best_w2v_value'] <0.45) & (result['best_ft_value'] <0.45) ]
result_equals = result[result['best_w2v'] == result['best_ft'] ]

# si el mejor de w2v esta entre los 3 mejores de ft
def check(element):
    if element.best_w2v in element.best3_ft and element.best_ft in element.best3_w2v:
        return True

    else:
        return False

result['contained'] = result.apply(check,axis = 1)
result_contained = result[result['contained'] == True]


result.boxplot(column = ['best_w2v_value'])
result.quantile(0.75)


#%%
import numpy as np
equals_list = []
ii = []
equals_contained_list = []
total = []
for i in np.arange(0.001,0.5,0.01):

    result_div = result[(result['best_glove_value'] <i) & (result['best_ft_value'] <i) ]
    total.append(len(result_div))

    result_equals = result_div[result_div['best_glove'] == result_div['best_ft'] ]
#    value_equals = (len(result_equals)/len(result_div))*100
    equals_list.append(len(result_equals))

    result_div['contained'] = result_div.apply(check,axis = 1)
    result_contained = result_div[result_div['contained'] == True]
#    value_contained = (len(result_contained)/len(result_div))*100
    equals_contained_list.append(len(result_contained))
#    equals_contained_list.append((len(result_contained)/len(result_div))*100)
    
    ii.append(i)
#%%
import matplotlib.pyplot as plt


plt.xlabel('Distance value of the mapping')  #, fontsize=18)
plt.ylabel('Number of mappings with a match')#, fontsize=16)
plt.plot(ii,equals_contained_list,marker='o', markerfacecolor='red', markersize=3, color='orange', linewidth=1, label="mapping match in the three bests")
fig = plt.plot(ii,equals_list,marker='o', markerfacecolor='blue', markersize=3, color='skyblue', linewidth=1, label="best mapping match")
#plt.ylim([0, 110]) 
plt.plot(ii,total ,marker='o', markerfacecolor='darkgreen', markersize=3, color='lightgreen', linewidth=1, label="total of mappings")
#plt.hlines(y = 772, xmin=0, xmax=0.5 ,linestyle='dashed',color='gray', linewidth=1)
plt.legend(loc="upper left")
plt.title("Equivalent mappings (word2vec vs fastText)") 
fig
plt.savefig('w2vec_vs_fasttext.png', dpi=150)


from collections import Counter
result_new = result[(result['best_w2v_value'] >0.4809) & (result['best_ft_value'] >0.4809) ]
result_new = result[(result['best_w2v']  != result['best_ft'] )]
w2v_res = dict(Counter(list(result_new['best_w2v'])))
w2v_resft = dict(Counter(list(result_new['best_ft'])))


p_o = 840/1104
p_e = 1/ 1104

(p_o - p_e)/(1-p_e)

#%%

sklearn.metrics.cohen_kappa_score(list(result['best_w2v_value']), list(result['best_ft_value']))


