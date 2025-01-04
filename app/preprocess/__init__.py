
import pandas as pd
import numpy as np

# find max length of ingadient list
def find_max_length(data):
    max_len = 0
    for recipe_id, recipe in data.items():
        if 'ingredients' in recipe:
            max_len = max(max_len, len(recipe['ingredients']))
    print(f'ingredients max num: {max_len}')
    return max_len



def standardize(recipes,required_fields ):
    """
    input: 
    recipes: dictionary of recipes
    required_fields: list of fields that each recipe should have
    ingredients_max_length: maximum number of ingredients in a recipe
    
    Standardize Fields:ensure consistent structure in each recipe
    flatten ingredients list into separate columns
    Ensure that each recipe follows the same structure (represented with consistent fields)
    return:
    recipes: dataframe of recipes with consistent structure
    ids_without_ingredients: list of keys for recipes without ingredients
    
    """
    # flatten ingridients list into separate columns
    ingredients_col = ''
    ingredients = {f'{ingredients_col}{i}': None for i in range(find_max_length(recipes))}
    
    required_fields.remove('instructions')

    ids_without_instructions = []
    ids_without_ingredients = []
    c = []
    for recipe_id,recipe in recipes.items():
        if 'instructions' not in recipe  :
            ids_without_instructions.append(recipe_id)
            continue
        if 'ingredients' not in recipe or not recipe['ingredients']:
            ids_without_ingredients.append(recipe_id)
            continue
        
        for field in required_fields:
            if field not in recipe:
                recipe[field] = None  # Assign None if a required field is missing
                c.append(field)
            elif recipe[field] is None:
                c.append(field)
                
        # Flatten ingredients list into separate columns and remove the original 'ingredients' field
        # ingredient 0 saves as column '0' and so on
        if 'ingredients' in recipe.keys() and recipe['ingredients'] is not None:
            
            ingredients_cur =ingredients.copy()
            
            ingredients_cur.update({f'{ingredients_col}{i}': recipe['ingredients'][i] for i in range(len(recipe['ingredients']))})
            recipe.update(ingredients_cur)
            del recipe['ingredients']

        # recipes[recipe_id] = recipe
        # print(1)
    print(f'fields which may have null value: {np.unique(c)}')
    print(f'recipes without instructions (removed from data): {ids_without_instructions}')
    print(f'recipes without ingredients (removed from data): {ids_without_ingredients}')
    [recipes.pop(recipe_id) for recipe_id in set(ids_without_instructions+ids_without_ingredients)]
    recipes_df = pd.DataFrame.from_dict(recipes, orient='index')

    return recipes_df,ingredients.keys()


# -------------------------------


import pandas as pd
import string
import re

def split_un_words(text):
    '''
    Function to split words starting with 'un' into 'un' and the rest of the word.
    For example, 'unsalted' becomes ['un', 'salted'].
    '''
    # Split the input text into words
    words = text.split()

    # Check if the word starts with 'un' and is followed by alphabetic characters
    # Split the word into 'un' and the rest of the word
    result = [word if not (word.lower().startswith('un') and len(word) > 2) else ' '.join(['un', word[2:]]) for word in words]

    # Join the result into a single string or return as list of words
    return ' '.join(result)


def split_number_and_word(word):
    '''
    Function to split a word containing a number and a word, regardless of whether the 
    number comes before or after the word (e.g., '2an' -> ['2', 'an'] or 'an2' -> ['an', '2']).
    Also handles fractions like '1/2cup' -> ['1/2', 'cup'].
    '''
    # Match the pattern where the number can be a fraction or a whole number before letters
    match = re.match(r'(\d+/\d+|\d+)([a-zA-Z]+)', word)  # Number (fraction or whole) before letters
    if match:
        return [match.group(1), match.group(2)]
    
    # If no match, check if the number is after the word (letters before number)
    match = re.match(r'([a-zA-Z]+)(\d+/\d+|\d+)', word)  # Letters before number (fraction or whole)
    if match:
        return [match.group(1), match.group(2)]
    
    # If no match is found, return the word as is
    return [word]
# Apply the clean_text function to each row in the 'text_column'
# Define the clean_text function
def clean_text(text,):
    '''
    Function to clean text by:
    1. remove encoding characters like \xad, \u00ad
    2. seperate punctuation,
    3. Remove words like 'ADVERTISEMENT' and other non-recipe related terms.
    4. converting to lower case and remove leading/trailing whitespaces.
    '''
    # Define the set of punctuation characters to remove (including special symbols like ¿, °)
    # %&$ *+-°º–
    # in dict: ¼¾½ ----todo:°º
    # string_punctuation = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'"#string.punctuation
    text = text.lower().strip()
    # .translate(str.maketrans("", "", custom_punctuation))
    remove_terms = ['\xad', '\u00ad', '¿','®'] + ['advertisement']
    for char in remove_terms:
        text = text.replace(char, '')
    # seperate punctuation characters from the words by adding spaces around them - Use regular expression
    string_punctuation = '!"#$%&()*+,-:;<=>?@[\\]^_`{|}~'#string.punctuation (except: / ' . which should be handled separately)
    text = re.sub(r'([' + re.escape(string_punctuation) + r'])', r' \1 ', text)
    # Regex to separate '.' from words (except in numbers)
    text = re.sub(r'([' + re.escape('.') + r'])(?!\d)', r' \1 ', text)
    
    return text if text else None
    # for char in string.punctuation:
    #     text = text.replace(char, ' '+ char + ' ')
    
# 
                
def normalize_text(df, columns_to_clean):
    '''
    function to clean text in the specified columns of the input dataframe.
    1. clean_text: remove encoding characters like \xad, \u00ad, seperate punctuation, remove words like 'ADVERTISEMENT' and other non-recipe related terms, converting to lower case and remove leading/trailing whitespaces.
    2. split_number_and_word: split a word containing a number and a word, regardless of whether the number comes before or after the word (e.g., '2an' -> ['2', 'an'] or 'an2' -> ['an', '2']).
    3. split_un_words: split words starting with 'un' into 'un' and the rest of the word. For example, 'unsalted' becomes ['un', 'salted'].
    4. convert_words: convert words in the text to a specified format using a conversion dictionary.
    '''
    for column in columns_to_clean:
        # print(column)
        df[column] = df[column].copy().apply(lambda x: clean_text(x) if pd.notna(x) else x)
        df[column] = df[column].apply(
            lambda text: ' '.join([item for word in text.split() for item in split_number_and_word(word)]) if pd.notna(text) else text)
        df[column] = df[column].copy().apply(lambda x: split_un_words(x) if pd.notna(x) else x)
    return df