#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 17:29:00 2020

@author: Andrea Morales Garzón

Adaptation of recipes 
This file pre-processes the ingredients of the recipe, and looks for a mapping to the database.
The properties of the food are consulted to see if there is an incompatibility
with the restriction, and a new mapping is made that allows to map the ingredient
to one of those that are allowed.
 
"""

from gensim.models import KeyedVectors
from gensim.models.phrases import Phraser
from gensim.parsing.preprocessing import preprocess_string, remove_stopwords, stem_text
import gensim
import pandas as pd
import numpy as np
from fjaccard import fjaccard_extended
import ast
import random
import json

# load language models
CUSTOM_FILTERS = [remove_stopwords, stem_text]
CUSTOM_FILTERS_2 = [remove_stopwords]
modelo_guardado = KeyedVectors.load("../models/v2/modelo3")
bigram_loaded = Phraser.load("../models/v2/my_bigram_model.pkl")

df_idiet = pd.read_excel("../data/inglesa-labeled_reducida_vegan_terminada.xlsx")

def funcc(tex):
    x = 'Yes'
    return x


df_idiet['no_restriction'] = df_idiet['Main food description'].apply(funcc)

#%%
# apply word embedding text preprocessing to the food to get their representation
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


# Function to mapping ingredient to food database
def get_DB_equivalent(idiet_item_list, bd_names_ , bd_names_mapping , model, number_instances = False):
    
    # get similarity between ingredient and dataset foods
    vector_similarity = np.zeros(len(bd_names_mapping))
    for i,item in enumerate(bd_names_mapping):
        s = fjaccard_extended(idiet_item_list, item, modelo_guardado)
        vector_similarity[i] = s

    # identify the most accurate
    sorted_list = np.argsort(vector_similarity)


    # get the bestx mappings (in this case we obtain 10)
    if number_instances == True:
        most_similar = [ bd_names_[sorted_list[i]] for i in range(10) ]
        value_most_similar = [ vector_similarity[sorted_list[i]] for i in range(10) ]
        
        # inf distance value is infinity or very high, we consider there is no similar ingredient in the database
        for i,value in enumerate(value_most_similar):
            if value == np.Infinity:
                most_similar[i] = 'No matches'
            if value > 44.0:
                most_similar[i]  = 'No matches'
    else:
        most_similar = bd_names_[sorted_list[0]]
        value_most_similar = vector_similarity[sorted_list[0]]    
        if value_most_similar == np.Infinity:
            most_similar = 'No matches'


    alternatives = [ bd_names_[sorted_list[i]] for i in range(10) ]
    print(alternatives)

    return most_similar, value_most_similar, alternatives

#%%

def get_accurate_mapping(i,model,bigram,db,nutritional_data,bd_names_processed):
    ingredient_processed = preprocess_recipe(i)
    print(ingredient_processed)
    mapping_idiet, value_mapping, alternatives_  = get_DB_equivalent(ingredient_processed,bd_names_=db,bd_names_mapping=bd_names_processed,model=model,number_instances=False)
    mapping = nutritional_data[nutritional_data['Main food description'] == mapping_idiet]
    
    return mapping, mapping_idiet, value_mapping, alternatives_ 


#%%



def get_adapted_recipe(recipe,model,bigram,db,nutritional_data,restriction):
    
    # preprocessing recipe data
    bd_names_processed = [preprocess_recipe(x) for x in db]
    
    
    list_recipe_ingredients = []

    # get recipe ingredients
    recipe_ingredients = recipe['ingredients']
    
    for i in recipe_ingredients:
        print("......")
        print(i)
        
        # for each ingredient in recipe, we search for the most accurate mapping
        mapping, mapping_idiet, value_mapping, others= get_accurate_mapping(i,model,bigram,db,nutritional_data,bd_names_processed)

        modified_action = 'no'
        adapted_ing = ""
        
        if mapping_idiet != 'No matches':
            
            mapping = mapping.iloc[0]

            if mapping[restriction] == "No" and value_mapping <0.9:
                print("entra")
                modified_db = nutritional_data[nutritional_data[restriction] == "Yes"]
                bd_names_mod = list(modified_db['Main food description'])
                bd_names_mod_processed = [preprocess_recipe(x) for x in bd_names_mod] 
                mapping, adapted_ing, value_mapping, others = get_accurate_mapping(i,model,bigram,bd_names_mod,modified_db,bd_names_mod_processed)

                modified_action = 'yes'
                
            if value_mapping > 0.9:
                value_mapping = None
        else:

            value_mapping = None
            

        list_recipe_ingredients.append({'name':i, 'modified':modified_action,'adapted':adapted_ing, 'others':others})
    return list_recipe_ingredients
                


#%%  

# ejemplo

usda_ingredients = pd.read_excel("../data/inglesa-labeled_reducida_vegan_terminada.xlsx")
bd_names = list(usda_ingredients['Main food description'])



df_rcp = pd.read_csv('../data/RAW_recipes-foodcom-kaggle.csv')

dict_rcp = df_rcp.to_dict('records')
##

random.seed(12345)
xx = random.sample(dict_rcp,20)

#%%
    
# order results (used for preference type of adaptations)
    
def ordenar(list_mappings,nutrient):
    list_mappings = list_mappings[2:5]
    print(len(list_mappings))
    valores_nutricionales = np.zeros(len(list_mappings))
    for i,map_ in enumerate(list_mappings):
        print(map_)
        item = usda_ingredients[usda_ingredients['Main food description'] == map_].iloc[0]
        print(item['Main food description'])
        if item[nutrient] == 'Tr':
            valores_nutricionales[i] = 0
        elif item[nutrient] != 'N':
            valores_nutricionales[i] = item[nutrient]
            print(valores_nutricionales[i])
        else: 
            valores_nutricionales[i] = np.nan
            
        print(valores_nutricionales)
        
    mean_value = np.nanmean(valores_nutricionales)
    valores_nutricionales = np.where(valores_nutricionales==np.nan, mean_value, valores_nutricionales) 
    print(mean_value)

    sorted_list = np.argsort(valores_nutricionales)
    print(sorted_list)
    res_ordenado = [list_mappings[i] for i in sorted_list ]

    return res_ordenado
    
        
list_prueba = ['Allspice, ground','Lime juice cordial, diluted','Langoustine, boiled']      
r_list = ordenar(list_prueba, 'Energy (kcal) (kcal)')  

#%%

def get_recipe_adaptation(recipe_,adaptation_type='no_restriction', kind='preferences', order=False):
    
    print(recipe_['name'])
    print(recipe_['ingredients'])
    rp_ = {"id":recipe_
           ['id'],'name':recipe_["name"],"ingredients":ast.literal_eval(recipe_["ingredients"]), "steps":ast.literal_eval(recipe_['steps']), 'description':recipe_['description'], 'type':kind}
    x = get_adapted_recipe(recipe=rp_,model=modelo_guardado,bigram=bigram_loaded,db=bd_names,nutritional_data=usda_ingredients,restriction=adaptation_type)
        
    
    if order:
        for i,element in enumerate(x):
            x[i]['others'] = ordenar(element['others'],'Energy (kcal) (kcal)')
        
        
    rp_['ingredients'] = x
    
    
    
    with open('../res/'+kind+'/data_recipe_'+rp_['name']+'.json', 'w') as fp:
        json.dump(rp_, fp)
    

    print("--")
    
    
#%%
for i in list(xx):
    print("-------------------------------------")
    get_recipe_adaptation(i,adaptation_type='no_restriction', kind='light',order=True)
    


#%%
