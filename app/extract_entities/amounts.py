import re
from warnings import simplefilter
import pandas as pd
import spacy

simplefilter(action="ignore", category=pd.errors.PerformanceWarning)
# Conversion dictionary for fractional values
measurement_amounts = {
    # fraction_to_decimal
    '¼': '0.25',
    '¾': '0.75',
    '½': '0.5',
    '1/4': '0.25',
    '1/8': '0.125',
    '1/2': '0.5',
    '3/4': '0.75',
    '1/3':'0.333',
    '2/3':'0.666',
    '3/8': '0.375',
    '5/8': '0.625',
    '7/8': '0.875'
    
    

    # 'pkg': 'package',
    # 'sliced': 'cut',
    # 'chopped': 'cut',
    # 'minced:': 'small cut',
    # 'finely': 'small',
    # 'freshly': 'fresh',
    # # 'tiny': 'small',
    # 'grated':'shredded',

    # # 'diced':'cubed'

}
import json
with open('measurement_units.json', 'r') as f:
    measurement_units = json.load(f)
    
# Load the spaCy model
nlp = spacy.load('en_core_web_sm')


# Function to convert string fractions to decimals in the text
def convert_amounts_to_numeric(text, conversion_dict):

    return ' '.join([' '+conversion_dict[word]+' ' if word in conversion_dict.keys() else word for word in text.split()])
    
def convert_units(text, conversion_dict):

    # Split the text into words
    converted_words = []
    words_before_convertion_list = []
    words_after_convertion_list =[]
    for word in text.split():
         # If the word matches a key in the dictionary, replace it, otherwise leave it as is
        if word in conversion_dict.keys():#if word is in the dictionary (its a unit)
            words_before_convertion_list.append(word)
            # word = ' '+conversion_dict[word]['unit']+' '#convert unit
            word = conversion_dict[word]['unit']#convert unit

            words_after_convertion_list.append(word)
        # converted_words.append(word)
    # Rejoin the words back into a string
    # text = ' '.join(converted_words)
    if not words_after_convertion_list:#return null insted of empty list
        words_before_convertion_list , words_after_convertion_list = None , None
    # return pd.Series([text, words_before_convertion_list , words_after_convertion_list ])
    return pd.Series([words_before_convertion_list , words_after_convertion_list ])

def find_numeric_amounts(text):
    # Use regular expressions to find all numbers in the text
    amounts = [float(match) for match in re.findall(r'\d*\.?\d+', text)]
    return None if not amounts else amounts

def convert_amounts_unit(units, amounts,measurement_units):
    units_conversion = units.copy() 
    units_conversion.loc[units.notnull()] = [measurement_units[u[0]]['conversion'] for u in units.loc[units.notnull()]]
    amounts.loc[amounts.notnull()] = [a[0] for a in amounts.loc[amounts.notnull()]]
    # convert only if units_conversion exists (some units may not have conversion such as pinch, dash)
    new_amounts = amounts.copy()
    new_amounts.loc[units_conversion.notnull()] = (units_conversion*amounts).loc[units_conversion.notnull()]
     
    return new_amounts
     
def extract_entities(df, columns_to_extract = []):
    # df['season'] = []*len(df)
    for column in columns_to_extract:
        try:
            df[f'{column}_ingredients'] = df[column].copy().apply(lambda x: extract_ingredient(nlp,measurement_units.keys(),x) if pd.notna(x) else x)

            new_columns = {f'{column}_units_orig':f'{column}_units_orig',
                        f'{column}_units_converted':f'{column}_units_converted',
                        f'{column}_amount_orig':f'{column}_amount_orig',
                        f'{column}_amount_converted':f'{column}_amount_converted',
                        }
            df[[ new_columns[f'{column}_units_orig'],  new_columns[f'{column}_units_converted'],]] = df[column].apply(lambda x: convert_units(x, measurement_units) if pd.notna(x) else pd.Series([x, None]))
            df[column] = df[column].copy().apply(lambda x: convert_amounts_to_numeric(x, measurement_amounts) if pd.notna(x) else x)
            df[new_columns[f'{column}_amount_orig']] = df[column].copy().apply(lambda x: find_numeric_amounts(x) if pd.notna(x) else x)
            df[new_columns[f'{column}_amount_converted']] = convert_amounts_unit(df[new_columns[f'{column}_units_orig']].copy(), df[new_columns[f'{column}_amount_orig']].copy(),measurement_units)

            # original values - amount and units - not required so commented: used for debugging
            # df[f'{column}_orig'] = df.apply(lambda row: {key: row[key] for key in 
            #                                                [new_columns[f'{column}_amount_orig'],new_columns[f'{column}_units_orig'],]
            #                                                }, axis=1)
            df[f'{column}_converted'] = df.apply(lambda row: {key: row[key] for key in 
                                                [new_columns[f'{column}_amount_converted'],new_columns[f'{column}_units_converted'],]
                                                }, axis=1)
            # rows with no units and no amounts are seasoning and should be set to None 
            ind = df[new_columns[f'{column}_units_orig']].isnull() & df[new_columns[f'{column}_amount_orig']].isnull() & ~df[column].isnull()
            df.loc[ind[ind].index,f'{column}_converted'],df.loc[ind[ind].index,f'{column}_ingredients'] = None,None
            
            # drop temporary columns used for extraction
            df.drop(new_columns.values(),inplace=True,axis=1)
        except Exception as e:
            print(e)
            print(f'error in column {column}')
        # break
    return df


def extract_ingredient(nlp,units,text):
    '''
    extract_ingredient: 
        Extracts the nouns from a text using spaCy
        tokens we consider nouns - tokens of type NOUN and tag NN (Noun, singular or mass such as "dog")
        nouns which are not unit of measurement (not in measurement_units dictionary) are considered as ingredients
    Input:
        text: The text to process
        nlp: The spaCy model
    Output:
        ingredients: A list of the ingredients in the text
    
    '''
    nouns = []
    for token in nlp(text):
        if token.pos_=='NOUN' and token.tag_=='NN':
            nouns.append(token.text)
            # print(f"Word: {token.text}, POS: {token.pos_}, Tag: {token.tag_}, Ent: {token.ent_type_}")
    # remove nouns which are units of measurement
    return [noun for noun in nouns if noun not in units]

import re

def sort_columns(df):
    # Step 1: Define the fixed non-numeric columns (as specified)
    non_numeric_columns = ['title', 'instructions', 'picture_link', 'website']

    # Step 2: Separate numeric columns (those that start with digits)
    numeric_columns = [col for col in df.columns if re.match(r'^\d+', col)]

    # Step 3: Sort numeric columns based on the numeric part at the start (ignoring suffixes)
    def sort_natural(col):
        # Extract the leading number from the column name
        match = re.match(r'(\d+)', col)
        if match:
            return int(match.group(1))  # Convert to integer for proper sorting
        return float('inf')  # If not a numeric column, put it at the end

    # Step 4: Sort numeric columns
    numeric_columns_sorted = sorted(numeric_columns, key=sort_natural)

    # Step 5: Combine non-numeric columns and sorted numeric columns
    sorted_columns = non_numeric_columns + numeric_columns_sorted

    return sorted_columns