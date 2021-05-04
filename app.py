import os
import pytesseract as pt 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import inflect
import regex

import streamlit as st
import time
import pandas as pd

# comment out, only needed for specific runtime
pt.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def euc_dist(food1, food2, ingredient_coor):
  food1_x = ingredient_coor[ingredient_coor['name'] == food1]['x'].values[0]
  food1_y = ingredient_coor[ingredient_coor['name'] == food1]['y'].values[0]
  food2_x = ingredient_coor[ingredient_coor['name'] == food2]['x'].values[0]
  food2_y = ingredient_coor[ingredient_coor['name'] == food2]['y'].values[0]
  return np.sqrt((food1_x - food2_x)**2 + (food1_y - food2_y)**2)

#takes in word and returns n most similar ingredients
def most_similar(word, n, ingredient_coor):
  word = word.lower()
  if word not in np.array(ingredient_coor['name']):
    return np.array([False])
  #print(np.array(ingredient_coor['name']))
  ingredient_coor['dist'] = [euc_dist(word, i, ingredient_coor) for i in np.array(ingredient_coor['name'])]
  ingredients = ingredient_coor.sort_values('dist', ascending = True)
  return ingredients.iloc[1:n+1]['name'].values

#takes a string input of a food/ingredient name and returns the corresponding 
#allergy information if it is found in the allergies table.
def search_food(food, allergies):
  engine = inflect.engine()
  #print(type(allergies))
  if engine.singular_noun(food) != False:
    food = engine.singular_noun(food)
  if allergies['Food'].str.contains(food.capitalize()).any() == False:
    return False
  return True

def lookup(menu_string, allergies, ingredient_coor):
  split = menu_string.split('\n\n')
  item_names = []
  ingredient_matches = []
  potential_matches = []
  for item in split:
    item_names.append(item.split('\n')[0])
    #print(item.split('\n'))
    ingredients = []
    potential_found = []
    for string in item.split('\n'):
      for word in string.split(' '):
        #print(word)
        word = regex.sub("[^a-zA-Z]+", "", word.lower())
        if search_food(word, allergies) == True:
          ingredients.append(word)
        else:
          potential = most_similar(word, 50, ingredient_coor)
          if potential.all() != False:
            for i in potential:
              if search_food(i, allergies) == True:
                potential_found.append(i)
    ingredient_matches.append(np.unique(np.array(ingredients)))
    potential_matches.append(np.unique(np.array(potential_found)))
  lookup_table = pd.DataFrame(data = {'Item Name': item_names, 'Ingredient Matches': ingredient_matches, 'Potential Allergen Matches' : potential_matches})
  return lookup_table

def edible(allergy_type, allergy_types):
  allergens = []
  for altype in allergy_type:
        allergens += (allergy_types[allergy_types['Allergy'] == altype]['Food'].iloc[0])
  return allergens

#menu_file.name, general_allergies, specific_allergies, food_data, allergy_types
def minus_allergens(menu_image, general_allergens, specific_allergens, food_data, allergy_types, ingredient_coor):
  menu_string = pt.image_to_string(menu_image, timeout=10)
  engine = inflect.engine()
  allergies = edible(general_allergens, allergy_types) + specific_allergens
  lookup_df = lookup(menu_string, food_data, ingredient_coor)
  allergen_included = []
  allergens_detected = []
  allergen_matches = []
  potential_included = []
  potential_detected = []
  for dish in lookup_df['Ingredient Matches']:
    alg = []
    inc = False
    for food in dish:
      if engine.singular_noun(food) != False:
        current_food = engine.singular_noun(food).capitalize()
      else:
        current_food = food.capitalize()
      if current_food in allergies:
        inc = True
        alg.append(current_food)
    allergen_included.append(inc)
    allergens_detected.append(alg)
  for dish in lookup_df['Potential Allergen Matches']:
    alg2 = []
    inc2 = False
    for food in dish:
      if engine.singular_noun(food) != False:
        current_food2 = engine.singular_noun(food).capitalize()
      else:
        current_food2 = food.capitalize()
      if current_food2 in allergies:
        inc2 = True
        alg2.append(current_food2)
    potential_included.append(inc2)
    potential_detected.append(alg2)
  lookup_df['Allergen Included?'] = allergen_included
  lookup_df['Allergens Detected'] = allergens_detected
  lookup_df['Potential Allergen Included?'] = potential_included
  lookup_df['Potential Allergen Detected'] = potential_detected
  return lookup_df

def main():
	st.title('Alergi')
	st.write('_Making eating out **safer** and **accessible** for people with food allergies._')
	st.write('We use advance machine learning with FDA data to make sure you get the most accurate information about allergens in your food.')

	st.header('Profile Setup')
	general_allergies = st.multiselect('Select Allergies',options=['Nut Allergy', 'Oral Allergy Syndrome', 'Stone Fruit Allergy',
															       'Insulin Allergy', 'Allium Allergy', 'Histamine Allergy',
															       'Banana Allergy', 'Gluten Allergy', 'Legume Allergy',
															       'Salicylate Allergy', 'Broccoli allergy', 'Cruciferous Allergy',
															       'Ragweed Allergy', 'Milk allergy / Lactose intolerance',
															       'Mushroom Allergy', 'Hypersensitivity', 'Alpha-gal Syndrome',
															       'Poultry Allergy', 'Ochratoxin Allergy', 'Corn Allergy',
															       'Seed Allergy', 'Shellfish Allergy', 'Fish Allergy',
															       'Nightshade Allergy', 'Sugar Allergy / Intolerance', 'LTP Allergy',
															       'Citrus Allergy', 'Honey Allergy', 'Beer Allergy',
															       'Potato Allergy', 'Lactose Intolerance', 'Aquagenic Urticaria',
															       'Peanut Allergy', 'Mint Allergy', 'Rice Allergy', 'Pepper Allergy',
															       'Soy Allergy', 'Tannin Allergy', 'Thyroid'])

	specific_allergies = st.multiselect('Select Allergies',options=['Almond', 'Apple', 'Apricot', 'Artichoke', 'Asparagus', 'Avocado',
															       'Bamboo shoot', 'Banana', 'Barley', 'Bean', 'Blackberry',
															       'Black-eyed bean', 'Blueberry', 'Bonito', 'Broad bean', 'Broccoli',
															       'Brussels sprouts', 'Buckwheat', 'Burdock', 'Butter',
															       'Butter bean', 'Buttermilk', 'Button mushroom', 'Cabbage',
															       'Cacao bean', 'Canola oil', 'Carrot', 'Casein', 'Cattle',
															       'Cauliflower', 'Celery', 'Cheese', 'Cherry', 'Chestnut', 'Chicken',
															       'Chicory', 'Chinese cabbage', 'Coconut oil', 'Coffee bean', 'Corn',
															       'Corn oil', 'Cotton seed', 'Cranberry', 'Cream', 'Crustaceans',
															       'Cucumber ', 'Custard', 'Date', 'Deer', 'Duck', 'Eel', 'Egg plant',
															       'Eggs', 'Endive', 'Fructose', 'Garlic', 'Ghrkin', 'Ginger',
															       'Ginkgo nut', 'Globfish', 'Glucose', 'Goat', 'Grape', 'Grapefruit',
															       'Grapeseed oil', 'Green soybean', 'Groundnut oil', 'Guava',
															       'Honey', 'Hop', 'Horse', 'Horse Mackerel', 'Horseradish',
															       'Huckleberry', 'Ice cream', 'Japanese pear', 'Japanese persimmon',
															       'Japanese plum', 'Kale', 'Kidney bean', 'Kiwi', 'Konjac', 'Kyona',
															       'Lactose', 'Leek', 'Lemon', 'Lentil', 'Lettuce ', 'Lima bean',
															       'Lime', 'Loquat', 'Mackerel', 'Makuwauri  melon', 'Mango',
															       'Melons', 'Milk', 'Mineral water', 'Mitsuba', 'Mume plum',
															       'Mustard oil', 'Mustard Spinach', 'Nectarine', 'Nira', 'Okra',
															       'Olive oil', 'Onion', 'Orange', 'Orange pulp', 'Papaya', 'Parsley',
															       'Parsnip', 'Passion fruit', 'Peach', 'Peanut', 'Pear', 'Peas',
															       'Pecan', 'Pegia', 'Peppermint', 'Percifomes', 'Pig', 'Pineapple',
															       'Popcorn', 'Potato', 'Prune', 'Pumpkin', 'Qing-geng-cai', 'Quince',
															       'Radish leaf', 'Radish root', 'Rapeseed', 'Raspberry', 'Rice',
															       'Ricebran oil', 'Royal Jelly', 'Rye', 'Safflower seed', 'Salmon',
															       'Salsify', 'Sansho', 'Sea Bass', 'Sea Bream', 'Sesame seed',
															       'Shallot', 'Sheep', 'Shelled mollusc', 'Shiitake  mushroom',
															       'Shungiku', 'Sour cream', 'Soybean', 'Spearmint', 'Spinach',
															       'Squash', 'Strawberry', 'Sugar', 'Sugar beet', 'Sugarcane',
															       'Sultani', 'Sultapya', 'Sunflower oil', 'Sunflower seed',
															       'Sweet corn', 'Sweet Pepper', 'Sweet potato', 'Taro', 'Tea',
															       'Tetraodontiformes', 'Tomato', 'Trout', 'Tuna', 'Turkey',
															       'Turnip leaf', 'Turnip root', 'Vegetable oil', 'Walnut',
															       'Water melon', 'Watercress', 'Welsh', 'Wheat', 'Whey',
															       'White bean', 'Yam', 'Yogurt'])

	# additional_allergies = st.text_input('Additional Allergies')

	st.header('Allergy Check')
	# might be byte stream, Image(menu_file)
	menu_file = st.file_uploader("Upload Menu Image", type=['png','jpeg', 'jpg', 'gif']) 

	if menu_file is not None:
	    st.image(menu_file)

	submitted = st.button('Submit')

	if submitted:
		with st.spinner('Processing...'):
			## JESSIE: ALL CODE PROCESSING GO HERE
			food_data = pd.read_csv("FoodData.csv")
			allergy_types = food_data.groupby("Allergy", as_index = False).agg(list)[['Allergy','Food']]

			ingredient_coor = pd.read_csv('ingredient_coor.csv').drop('Unnamed: 0', axis = 1)
			ingredient_coor['name'] = ingredient_coor['name'].str.replace('[_]', ' ')

			df = minus_allergens(menu_file.name, general_allergies, specific_allergies, food_data, allergy_types, ingredient_coor) # TODO: MENU IMAGE, LIST OF ALLERGIES

		# DF is resulting dataframe
		if df[['Allergens Detected']].empty and df[['Potential Allergen Detected']].empty:
			st.balloons()
			st.success('No allergens found! Good to go :)')
		else:
			st.error('We found matched and potential allergens in the food. Here is a complete summary of our analysis:')
			st.dataframe(df)




if __name__ == '__main__':
	main()


