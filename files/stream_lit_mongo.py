
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 14:44:05 2020

@author: Andrea

"""


import streamlit as st
from streamlit import caching



import pandas as pd
import numpy as np

from pymongo import MongoClient
import os
import json



import streamlit as st
import streamlit.report_thread as ReportThread
from streamlit.server.server import Server
import time
import functools
import random
from datetime import datetime


from streamlit.report_thread import get_report_ctx
ctx = get_report_ctx()
seed = ctx.session_id
print(seed)

def get_session_id():
    session_id = ReportThread.get_report_ctx().session_id
    session_info = Server.get_current()._get_session_info(session_id)

    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")
    
    return session_id

# def fancy_cache(func=None, ttl=None, unique_to_session=False, **cache_kwargs):
#     """A fancier cache decorator which allows items to expire after a certain time
#     as well as promises the cache values are unique to each session.
#     Parameters
#     ----------
#     func : Callable
#         If not None, the function to be cached.
#     ttl : Optional[int]
#         If not None, specifies the maximum number of seconds that this item will
#         remain in the cache.
#     unique_to_session : boolean
#         If so, then hash values are unique to that session. Otherwise, use the default
#         behavior which is to make the cache global across sessions.
#     **cache_kwargs
#         You can pass any other arguments which you might to @st.cache
#     """
#     # Support passing the params via function decorator, e.g.
#     # @fancy_cache(ttl=10)
#     if func is None:
#         return lambda f: fancy_cache(
#             func=f,
#             ttl=ttl,
#             unique_to_session=unique_to_session,
#             **cache_kwargs
#         )

#     # This will behave like func by adds two dummy variables.
#     dummy_func = st.cache(
#         func = lambda ttl_token, session_token, *func_args, **func_kwargs: \
#             func(*func_args, **func_kwargs),
#         **cache_kwargs)

#     # This will behave like func but with fancy caching.
#     @functools.wraps(func)
#     def fancy_cached_func(*func_args, **func_kwargs):
#         # Create a token which changes every ttl seconds.
#         ttl_token = None
#         if ttl is not None:
#             ttl_token = int(time.time() / ttl)

#         # Create a token which is unique to each session.
#         session_token = None
#         if unique_to_session:
#             session_token = get_session_id()

#         # Call the dummy func
#         return dummy_func(ttl_token, session_token, *func_args, **func_kwargs)
#     return fancy_cached_func

#print(get_session_id())
#Title and text of the app

#title
st.title('Web app to validate our approach for the recipe adaptation problem (work in progress).')



### Sidebar

#Instructions
#st.sidebar.markdown("**Instructions:**")
#show_instructions = st.sidebar.checkbox("Show instructions", value = True)
    
#Reviewer data
st.sidebar.markdown("**Reviewer data:**")
#name
name_of_reviewer = st.sidebar.text_input("Introduce your name or ID or something")
#role
role = st.sidebar.selectbox(
        'Select your role',
        ('Expert', 'Regular user'),
        index=0,
    )


#st.sidebar.markdown('In this bar you can select the different type of recipes.\
 #           When finished, please press the send butto to submit the results.')
 
#Select the type of adaptation or help
st.sidebar.markdown("**Adapt a recipe:**")
adaptation_option = st.sidebar.selectbox(
    'Select a type of adaption',
    ('Non-restricted', 'Light adaptation', 'Vegetarian restriction', 'Vegan restriction',  'Form instructions'),
    index=4,
)


#Show help
if adaptation_option=='Form instructions':
    #caching.clear_cache()
    
    #introductory text
    st.markdown("Welcome! This app shows some results of the recipe\
    adaptation task. We created this app to validate the results\
    of our work. This work is still in progress and it will\
     be submitted to IEEE Access soon.")
    st.markdown("### Instructions ")
    st.markdown("- First, enter your name in the sidebar for identifying you. It can be anonymous. And please, you must enter your role either\
       expert or regular user.")
    st.markdown("- In this work, we adapt ingredients to specific user preferences. For that we use semantic relations between foods that able us to find ingredient substitutes. ")
    st.markdown("- You can find the different type of adaptations in the sidebar.")
    st.markdown("- Please, select each type of adaptation. Then, evaluate each recipe there. If you want to see the form instructions again you can\
    select in the *form instructions* option in the selection box. ")
    st.markdown("- You will see the original recipe on the left and the adapted one in the right.\
    The restricted ingredients are colored in red in the original recipe while the possible\
     the suggestion appears in green on the right. We show the top-3 suggestions.")
    st.markdown("- In the evaluation, you must say whether the adapted recipe makes sense or not or if\
       it coherent.\
    You must also punctuate it with a number between 0 and 5.\
     Finally, in each recipe, you can add your suggestions for enriching the adaptation in the text box.\
         You do not need to punctuate each possible ingredient change.\
             The mark is for a general adaptation using the suggested foods.")
    st.markdown("- When you finished some type of adaptation press the send button and the answers will be submitted.")
    st.markdown("- Select another type of recipe adaptation and repeat the process.")

           
############################################################################
#Auxiliary functions for writing the recipes

def original_recipe(col, modified, non_modified):
    """
    Show in markdown the original recipe in the selected col
    """
    
    #print non-modified ingredients in the original recipe
    ing = [col.markdown(str(i+1) + '. ' + x)  for i,x in enumerate(non_modified)]
    
    #print modified ingredients in the adapted recipe
    mod_ing = [col.markdown(str(i+1+len(non_modified)) + '. <span style="color:red">' + x + '</span>', unsafe_allow_html=True)  for i,x in enumerate(modified)]
    
    return None

    
def adapted_recipe(col, others, non_modified, others_nonmodified, type_, show_all_adaptations):
    """
    Show in markdown the adapted recipe in the selected col
    """ 
    if show_all_adaptations:
        #print non-modified ingredients in the adapted recipe
        ing = [col.markdown(str(i+1) + '. '  + x +' | <span style="color:green">'  + ' | '.join(others_nonmodified[i][1:3]) + '</span>', unsafe_allow_html=True)  for i,x in enumerate(non_modified)]
    else:
        ing = [col.markdown(str(i+1) + '. '  + x, unsafe_allow_html=True)  for i,x in enumerate(non_modified)]
        
    #print the suggestions for modified ingredients in the adapted recipe
    #if preferences selected, print from the second to the fourth elements
    if type_ == "preferences":
        mod_ing = [col.markdown(str(i+1) + '. <span style="color:green">' + ' | '.join(x[1:4]) + '</span>', unsafe_allow_html=True)  for i,x in enumerate(others)]
    #if any else print the top3 suggestions that satisfy the restriction
    else:
        mod_ing = [col.markdown(str(i+1+len(non_modified)) + '.  <span style="color:green">' + ' | '.join(x[:3]) + '</span>', unsafe_allow_html=True)  for i,x in enumerate(others)]
    
    return None

#auxiliary function for sampling recipes
#@fancy_cache(unique_to_session=True)
#@st.cache
def sample_recipes(list_recipes, number_of_recipes, seed=None):
    ctx = get_report_ctx()
    string = ctx.session_id
    print("string", string)
    seed_ = [i for i in string if i.isdigit()]
    
    print(seed_)
    seed_ = ''.join(seed_[:5])
    print(seed_)
    seed_ = int(seed_)
    np.random.seed(seed_)
    perm = np.random.permutation(len(list_recipes))
    return list_recipes[perm[:number_of_recipes]]

#############################################################################
#Read the data from Mongo
#@fancy_cache(unique_to_session=True)
@st.cache
def load_data():
    print("¡Estamos conectados a mLab!")
    user = str(os.environ.get("USER"))
    passw = str(os.environ.get("PASS"))
    database_name = str(os.environ.get("DATABASENAME"))
    collection_bd = str(os.environ.get("COLLECTION"))
    
    MONGODB_URI = "mongodb+srv://"+user+":"+passw+"@"+database_name+".0iqn3.mongodb.net/"+collection_bd+"+?retryWrites=true&w=majority"


    print("Succesfully connected to database")
    
    client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
    
    
    db = client.get_database("recipesdb")
    
    
    def get_all_predictions():
        return db.adapted_recipes.find({})
    
    cursor = get_all_predictions()
    actual_list_of_preds = []
    
    # We have to look in every document to the cursor to get a list of the
    # documents (we can't just print a cursor type)
    for document in cursor:
        next_dict = document
        next_dict.pop('_id')
        # we add the next document to the list of documents that we are
        # going to print
        actual_list_of_preds.append(next_dict)
        
    return actual_list_of_preds
###############################################################################

def show_recipes(recipes_, type_, name_of_reviewer, role):
     dict_results = []
     for i in range(len(recipes_)):
        #current recipe and its ingredients
        current_recipe = recipes_[i]
        current_ingredients = current_recipe["ingredients"]
        
        ##ingredients
        names = np.array([x['name'].capitalize() for x in current_ingredients])
        #modified or not (bool list)
        bool_modified = np.array([True if x['modified']=='yes' else False for x in current_ingredients])
        #list of others
        others = np.array([x['others'] for x in current_ingredients])
        
        #Showing the recipes in two columns
        
        #title for the current recipe
        st.markdown("## **Ingredients of recipe " + str(i+1) + '**: '+ current_recipe['name'])
        
        if type_ == 'vegan' or type_ == 'vegetarian':
            show_all_adaptations = st.checkbox("Show also suggestions for those ingredients that do not need adaptation", key = str(i)+type_)
        
        #two columns, original (left), adapted (right)
        col1, col2 = st.beta_columns(2) 
        
        #if preferences print the suggestion for all the ingredients
        if type_ == "preferences" or type_=="light":
            #we separate modified and non_modified
            non_modified = []
            modified = names
            #suggestions for modified ingredients
            modified_others = others
            
            col1.header("Original ingredients")
            original_recipe(col1, [], modified) #write the ingredients
            
            col2.header("Adapted ingredients")
            adapted_recipe(col2, modified_others, non_modified, '', type_, None)
        
        else:
            #we separate modified and non_modified
            non_modified = names[~bool_modified]
            modified = names[bool_modified]
            #suggestions for modified ingredients
            modified_others = others[bool_modified]
            non_modified_others = others[~bool_modified]
        
            col1.subheader("Original ingredients")
            original_recipe(col1, modified, non_modified) #write the ingredients
            
            col2.subheader("Adapted ingredients")
            adapted_recipe(col2, modified_others, non_modified, non_modified_others, type_, show_all_adaptations)
        
         #show instructions
        show_steps = st.checkbox('Show description and cooking instructions', key = str(i)+type_)
        if show_steps:
            st.markdown("**Description:**")
            st.markdown(current_recipe['description'].capitalize())
            st.markdown("**Coocking Instructions:**")
            steps = [st.markdown('- ' + x.capitalize())  for x in current_recipe['steps']]
            
        option_understand = st.selectbox(
            'Did you understand this recipe?',
            ('Yes','No'), key = str(i)+type_
        )
       
        #Options
        if role == "Expert":
            title_question = "Does the adaptation make sense?"
        elif role == "Regular user":
            title_question = "Do you see the adaptation coherent?"
        option = st.selectbox(
            title_question,
            ('Yes','No'), key = str(i)+type_
        )
        
        punctuation = st.slider('Punctuation (0:you hate this adaptation, 5:you love it) ', 0, 5, key = str(i)+type_)
        
        comments = st.text_input('There is another possibility that comes to your mind?', key = str(i)+type_)

        #append results
        dict_results.append(dict({'role': role, 'id': current_recipe['name'] , 'type_adaption': type_, 'mark': str(punctuation), 'correct': option, 'comments': comments, 'name_reviewer': name_of_reviewer, 'understand':option_understand}))
        

     return dict_results

##############################################################################

#Load the data
recipes = np.array(load_data())
type_ = np.array([x["type"] for x in recipes])

#Separate per type and sample some recipes
#TODO samplear las recetas
NUMBER_OF_RECIPES = 5
# vegan = sample_recipes(recipes[type_=="vegan"], NUMBER_OF_RECIPES)
# preferences = sample_recipes(recipes[type_=="preferences"], NUMBER_OF_RECIPES)
# vegetarian = sample_recipes(recipes[type_=="vegetarian"], NUMBER_OF_RECIPES)
# light = sample_recipes(recipes[type_=="light"], NUMBER_OF_RECIPES)

seed=0
vegan = sample_recipes(recipes[type_=="vegan"], NUMBER_OF_RECIPES, seed)
preferences = sample_recipes(recipes[type_=="preferences"], NUMBER_OF_RECIPES, seed)
vegetarian = sample_recipes(recipes[type_=="vegetarian"], NUMBER_OF_RECIPES, seed)
light = sample_recipes(recipes[type_=="light"], NUMBER_OF_RECIPES, seed)


#show recipes and request the reviewer's info
if adaptation_option == 'Non-restricted':
    #caching.clear_cache()
    st.markdown('# <span style="color:blue">  **Non-restricted ** </span> ', unsafe_allow_html=True)
    st.markdown("In this step, the system suggests similar ingredients alternatives to the ones \
                that appear in the recipe. For example, the system could suggest changing an orange with a tangerine.")
    dict_results_preferences = show_recipes(preferences, "preferences", name_of_reviewer, role)

if adaptation_option == 'Vegan restriction':
    #caching.clear_cache()
    st.markdown('# <span style="color:blue">  **Vegan recipes ** </span> ', unsafe_allow_html=True)
    st.markdown('In this step, the system adapts a recipe to vegan restrictions.\
                For example, if a recipe contains an “egg”, the system will identify \
                    it (see ingredients in red). The foods in green are the candidates \
                        for substituting the restricted ingredients.')  
    st.markdown('Notice that there is no change when all ingredients are vegan.\
                We added some optional ingredient suggestions (in green), \
                    in case they could give a better ingredient combination. \
                        To see them, you can click the button below the recipe title.')
    dict_results_vegan = show_recipes(vegan, "vegan", name_of_reviewer, role)
        
if adaptation_option == 'Vegetarian restriction':
    #caching.clear_cache()
    st.markdown('# <span style="color:blue">  **Vegetarian recipes ** </span> ', unsafe_allow_html=True)
    st.markdown('In this step, the system adapts a recipe to vegetarian restrictions. For example, if a recipe contains “meat”, \
                the system will identify it (see ingredients in red). The foods in green are the candidates for substituting\
                    the restricted ingredients.')
    st.markdown('Notice that there is no change when all ingredients are vegetarian.\
                We added some optional ingredient suggestions (in green), in case \
                    they could give a better ingredient combination. To see them,\
                        you can click the button below the recipe title.')
    dict_results_vegetarian = show_recipes(vegetarian, "vegetarian", name_of_reviewer, role)
    
if adaptation_option == 'Light adaptation':
    st.markdown('# <span style="color:blue">  **Light adaptation recipes ** </span> ', unsafe_allow_html=True)
    st.markdown('In this step, the system suggests ingredient substitutions favoring low-calorie ingredients. \
                You will see low-calorie alternatives that the system considers that could fit in the recipe.')
    
    dict_results_light = show_recipes(light, "light", name_of_reviewer, role)


#Button for sending the results
if adaptation_option != "Form instructions":
    st.markdown('<hr> ', unsafe_allow_html=True)
    st.markdown('### <span style="color:green"> **Once you finished, please send the recipes via this button**</span>' , unsafe_allow_html=True)
    if st.button('Send ' + adaptation_option):
        user = str(os.environ.get("USER"))
        passw = str(os.environ.get("PASS"))
        database_name = str(os.environ.get("DATABASENAME"))
        collection_bd = str(os.environ.get("COLLECTION"))
        
        MONGODB_URI = "mongodb+srv://"+user+":"+passw+"@"+database_name+".0iqn3.mongodb.net/"+collection_bd+"+?retryWrites=true&w=majority"
        
        client = MongoClient(MONGODB_URI, connectTimeoutMS=30000, retryWrites = False)
        
        db = client.get_database("recipesdb")
        #db.reviews.insert_many(dict_results)
        
        #send vegan
        try:
            vegan_write = [db.reviews.insert_one(x) for x in dict_results_vegan]
        except:
            pass
        
        #send preferences
        try:
            preferences_write = [db.reviews.insert_one(x) for x in dict_results_preferences]
        except:
            pass
        
        #send vegetarians
        try:
            vegan_write = [db.reviews.insert_one(x) for x in dict_results_vegetarian]
        except:
            pass
        
        try:
            light_write = [db.reviews.insert_one(x) for x in dict_results_light]  
        except:
            pass
            
        
        st.write('Thank you very much. Your results for *' + adaptation_option + '* have been submitted. Remember you have to repeat this process for the other adaptations.')

    
    
