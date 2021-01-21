# A word embedding-based method for unsupervised adaptation of cooking recipes

### Code of the method proposed for the paper titled "A word embedding-based method for unsupervised adaptation of cooking recipes" (in process to submit to IEEE ACCESS)

## Abstract

Studying food recipes is indispensable to understand the science of cooking. An essential problem in food computing is the adaptation of recipes to user needs and preferences. The main difficulty when adapting recipes is in determining ingredients relations, which are compound and hard to interpret. Word embedding models can catch the semantics of food items in a recipe, helping to understand how ingredients are combined and substituted. In this work, we propose an unsupervised method for adapting ingredient recipes to user preferences. To learn food representations and relations, we create and apply a specific-domain word embedding model.  In contrast to previous works, we not only use the list of ingredients to train the model but also the cooking instructions. We enrich the ingredient data by mapping them to a nutrition database to guide the adaptation and find ingredient substitutes. We performed three different kinds of recipe adaptation based on nutrition preferences, adapting to similar ingredients, and vegetarian and vegan diet restrictions. With a 95% of confidence, our method can obtain quality adapted recipes without a previous knowledge extraction on the recipe adaptation domain. Our results confirm the potential of using a specific-domain semantic model to tackle the recipe adaptation task.

## Summary

This repo contains the code and materials used for the paper "A word embedding-based method for unsupervised adaptation of cooking recipes". A detailed explanation of the tree directory is detailed below.

## Description of the repo
- [Streamlit app code for validating recipes]():
- [Data used for the experiments](https://github.com/andreamorgar/recipe-adaptation/blob/main/data):
- [Code](https://github.com/andreamorgar/recipe-adaptation/blob/main/files):
  - [Obtain step preparations plain text](https://github.com/andreamorgar/recipe-adaptation/blob/main/files/create_plain_recipe_text.py):
  - [Distance metric implementation](https://github.com/andreamorgar/recipe-adaptation/blob/main/files/fjaccard.py)
  - [Word embedding](https://github.com/andreamorgar/recipe-adaptation/blob/main/files/word_embedding.py)
  - [Word embedding comparison](https://github.com/andreamorgar/recipe-adaptation/blob/main/files/word-embedding-comparative.py)
  - [Code for recipe adaptation method](https://github.com/andreamorgar/recipe-adaptation/blob/main/files/recipe_adaptation.py)

### Instructions
- To get adapted recipes, firstly you need to download a recipe dataset. We recommend to use Food.com dataset available in Kaggle so as to not have to change any code ( [download here](https://www.kaggle.com/shuyangli94/food-com-recipes-and-user-interactions?select=RAW_recipes.csv))
- Then, adapting recipe following the code in here [here](https://github.com/andreamorgar/recipe-adaptation/blob/main/files/recipe_adaptation.py).


  
- If you only want to use the word embedding models, click [here](https://github.com/andreamorgar/recipe-adaptation/blob/main/models) to the trained food word embeddings.
- If you only want to use the corpus dataset, click [here](https://github.com/andreamorgar/recipe-adaptation/blob/main/data).