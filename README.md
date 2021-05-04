# Alergi
Making eating out safer and accessible for people with food allergies.

Alergi is an easy to use web application that allows users to input their restrictions in any language along with an image of a menu in order to receive a list of items from that menu which fit their dietary needs. Additionally, our ML model will measure the semantic similarity between words to suggest other items which may also be unsafe to consume. Just from their phones, users will be equipped with the confidence to go out and eat without worrying about their restrictions getting in the way.

We utilize a Food2vec machine learning model to identify ingredients of dishes. Food2vec is based on a quintessential natural language processing technique: word2vec. The word2vec algorithm uses a neural network model to learn word associations from a large corpus of text. Once trained, such a model can detect synonymous words or suggest additional words for a partial sentence. Similarly, food2vec vectorizes food items & ingredients in a multi-dimensional space and we are able to use non-linear dimensionality reduction techniques & advanced clustering algorithms to identify ingredients for any and all dishes. This enables us to match user allergies to potential allergens in the food.

# Usage
Once the site is launched, the user can select from a dropdown menu of common allergy groups, or additionally input specific ingredients they would like to avoid. Upload an image of a menu in any language, and submit for a detailed summary of direct and potential allergen matches.

# Implications

# Project Status
Currently, the output formatting is simply a comprehensive dataframe. Although we believe that this offers the most complete information for the user (which is the priority with such high risks involved in incomplete information involving severe food allergens), this is difficult to read off directly. In the future, we will create additional UI improvements that will present the necessary information in a more legible and aesthetically pleasing form.

