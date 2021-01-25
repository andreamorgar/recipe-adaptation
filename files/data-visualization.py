#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 11:28:47 2021

@author: andrea
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 22:29:56 2020

@author: Andrea Morales-Garzón
"""

import pandas as pd
import ast
import numpy as np
import matplotlib.pyplot as plt


try:
    df = pd.read_csv('../data/reviews24_01_2021--22-11-23.csv', sep=';')

    
    # all the data is in one column, we need to obtained in a correct format
    data = list(df['0'])
    
    
    # data is in str, we use ast to read the literals
    data_final = [ast.literal_eval(i) for i in data]
    
     
    # obtain reviewers number 
    reviewers = [i['name_reviewer'] for i in data_final]
    reviewers_unique = list(set(reviewers))
    # we can get how many responses have sent each user
    results = {}
    for i in data_final:
        if i['name_reviewer'] in results.keys():
            results[i['name_reviewer']] += 1
        else:
            results[i['name_reviewer']] = 1
            
    
    # dataframe in correct order
    df = pd.DataFrame(data_final)
    
    # suprime those "testing" reviews (sent only for test the database working)
    df = df[df['name_reviewer'] != 'Prueba']
    df = df[df['name_reviewer'] != 'PRUEBA']
    
    # we also remove those reviews sent with lack of understanding for remove the
    # bias derived from bad understanding of the recipe
    df = df[df['understand'] == 'Yes']
    
    #%%
    
    print("Percentage of correct adaptations: " + str(len(df[df['correct'] == 'Yes'])/len(df)))
    
    #%%
    
    df['mark'] = df['mark'].astype(float)
    
    # primero obtenemos los nombres de las recetas
    recipe_names = list(set(list(df['id'])))
    
    mean_marks = {}
    for i in recipe_names:
        
        df_i = df[df['id'] == i]
        marks = np.array(list(df_i['mark']))
        print(marks)
        mean_marks[i] = np.mean(marks)
        
    
    mean_marks_df = pd.DataFrame.from_dict(mean_marks, orient='index', columns=['mark'])
    print("Percentage of adequated adaptations: " + str(len(mean_marks_df[mean_marks_df['mark'] >= 2.5])/len(mean_marks_df)))
    
    
    
    #%%
    
    # to study the number of adequate adaptations per adaptation type
    def get_from_adaptation_type(type_adapt = 'light'):
        print("------------------")
        print("Adaptation type: " +type_adapt)
        recipe_names = list(set(list(df['type_adaption'])))
        
        df_adapt = df[df['type_adaption'] == type_adapt]
        recipe_names = list(set(list(df_adapt['id'])))
        
        mean_marks = {}
        for i in recipe_names:
            
            df_i = df_adapt[df_adapt['id'] == i]
            marks = np.array(list(df_i['mark']))
            mean_marks[i] = np.mean(marks)
            
        mean_marks_df = pd.DataFrame.from_dict(mean_marks, orient='index', columns=['mark'])
        print("Number of recipes: " + str(len(mean_marks_df)))
        print("número de recetas aprobadas: " + str(len(mean_marks_df[mean_marks_df['mark'] >= 2.5]))) 
        
    get_from_adaptation_type()    
    get_from_adaptation_type('preferences')    
    get_from_adaptation_type('vegetarian')    
    get_from_adaptation_type('vegan')
    
    #%%
    #mean review mark per type of adaptation
    def get_average_mark(type_adapt = 'light'):
        print("------------------")
        print("Adaptation type: " +type_adapt)
        recipe_names = list(set(list(df['type_adaption'])))
        
        df_adapt = df[df['type_adaption'] == type_adapt]
        recipe_names = list(set(list(df_adapt['id'])))
        marks = list(df_adapt.mark)
        print("Total of recipes: " + str(len(marks)))
        print("Mark: " + str(np.mean(marks)))
        return np.mean(marks)
    
    
    #%%
    
    # show the barplot of the review marks per adaptation type
    import seaborn as sns
    sns.set_style("whitegrid")
    df_visualization = df[['type_adaption','mark']]
    df_visualization['type_adaption'].replace('preferences','similar-based',inplace=True)
    df_visualization.columns = ['type','mark']
    sns.set_context("paper", font_scale=1.5) 
    ax = sns.barplot(x="type", y='mark', data=df_visualization, capsize=.2, order=['similar-based','light', 'vegetarian', 'vegan'])
    ax.axhline(2.5, ls='--',c='black')
    ax.set(ylim=(0, 5))
    #save image
    plt.savefig('../images/myimage3.png', format='png', dpi=1200)
    
    
    
    #%%
     
    sns.set_context("paper", font_scale=1.0) 
    df['type_adaption'].replace('preferences','similar-based',inplace=True)
    
    list_ordering = ["similar-based","light","vegetarian","vegan"]  
    df["type_adaption"] = pd.Categorical(df["type_adaption"], categories=list_ordering)
    
    df['Average mark'] = df.groupby('id', sort=False)['mark'].transform('mean')
    
    df_sub = df[['Average mark','id','type_adaption']].drop_duplicates()
    df_sub.columns = ['mark','id','type']
    
    g = sns.FacetGrid(df_sub, col="type", hue="type", height=4, aspect=.56, palette='tab10')
    
    g.map(sns.distplot, "mark", bins=[0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5],norm_hist=True)
    plt.xlim(0,5)
    
    g.savefig('../images/myimage.png', format='png', dpi=1200)
except:
    print("FILE ERROR: You have to load a reviews.csv file")