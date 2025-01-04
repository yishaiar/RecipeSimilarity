import os
import requests
import json
import zipfile
from pandas import notna
def download_zip(data_dir,url, ):
    # # Create the directory if it doesn't exist
    # if not os.path.exists(data_dir):
    #     os.makedirs(data_dir)
    
    # Extract the file name from the URL
    filename = url.split('/')[-1]
    file_path = os.path.join(data_dir, filename)
    
    # Send a GET request to the URL to fetch the ZIP file
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Write the content to a local file
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"ZIP file downloaded successfully to: {file_path}")
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")
        
        


def parse_json(zip_file_path,load_all=False,LEN=100):
    '''
    Function to parse a ZIP file containing multiple JSON files and merge them into a single dictionary.
    zip_file_path: str, path to the ZIP file
    load_all: bool, if True, load all the keys from the JSON files, otherwise load a subset of keys
    LEN: int, number of keys to load from each JSON file if load_all is False
    '''
    
    # Initialize an empty dictionary to store the data
    data = {}    

    # Open the ZIP file and process its contents
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        # Iterate over the files in the ZIP archive
        init = 0
        for fname in zip_ref.namelist():
            # Skip files that are not JSON files
            if not fname.endswith('.json'):
                continue

            # Read the JSON file content from the ZIP archive
            with zip_ref.open(fname) as file:
                tmp = json.load(file)
            # Remove empty keys (recipes) from the dictionary
            tmp = {key: tmp[key] for key in tmp.keys() if len(tmp[key]) > 0}

            # add the website taken from and the id as a values in the dictionary
            website = fname.split('_')[-1].split('.')[0]
            # 'recipe_id':key
            [tmp[key].update({'website': website,}) for key in tmp.keys()]
            # change dictionary key to numeric value
            tmp = {i: tmp[key] for i,key in enumerate(tmp.keys(),init)}
            

                
            # # Extract the first key and print the corresponding item
            key = list(tmp.keys())[0]
            # tmp = {key: tmp[key]}
            print(tmp[key].keys())
            
            if not load_all:# load only 100 keys from the each file
                keys = list(tmp.keys())[:LEN]
                tmp = {key: tmp[key] for key in keys}
            
            data.update(tmp)
            init = len(data)
            print(f'{fname} len:', len(tmp))
            print('total data len:', len(data))
            


    # At this point, 'data' contains all the merged JSON data
    return data


# # Function to print recipe details
# def print_recipe(recipe_id, recipe):
#     # print(recipe.keys())
#     print(f"Recipe ID: {recipe_id}")
#     print(f"Title: {recipe['title']}")
#     print("Ingredients:")

#     for key in [key for key in recipe.keys() if 'ingredient' in key]:
#         if recipe[key]:# check if the key is not empty
#             print(f" - {recipe[key]}")
    

            

#     print("Instructions:")
#     print(recipe['instructions'])
#     print(f"Picture Link: {recipe['picture_link']}")
#     print(f"website: {recipe['website']}")
#     print("\n" + "-"*40 + "\n")

# Function to print recipe details from a pandas Series
def print_recipe(recipe):
    print(f"Title: {recipe['title']}")
    print("Ingredients:")

    # Assuming ingredients are stored as a string or list in columns like 'ingredient1', 'ingredient2', etc.
    for column in recipe.index:
        
        if 'ingredient' in column.lower() :  # Checking for any column name that contains 'ingredient'
            ingredient = recipe[column]
            if type(ingredient) == list:
                for i in ingredient:
                    print(f" - {i}")
            elif notna(ingredient) :  # Check if the ingredient is not NaN (empty)
                print(f" - {ingredient}")
    
    print("Instructions:")
    print(recipe['instructions'])
    print(f"Picture Link: {recipe['picture_link']}")
    print(f"Website: {recipe['website']}")
    print("\n" + "-"*40 + "\n")