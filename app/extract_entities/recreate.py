def formatted_ingrediants(row, column):
    '''Combine values from counts and ingrediants to a single sentence with consisitent format'''
    # try:
    col1 = f'{column}_ingredients'
    col2=f'{column}_converted'
    if not row[col1]:
        return None
    amounts = row[col2][f'{column}_amount_converted']
    units = '' if row[col2][f'{column}_units_converted'] is None else row[col2][f'{column}_units_converted'][0]
    ingredients = ' '.join([word for word in row[col1]])
    sentence = f"{amounts} {units} {ingredients}."
    return sentence
    
    # except Exception as e:
    #     return None
    

def recreate_ingrediants_from_entities(df,ingredients_columns):
    '''
    This function takes a dataframe and a list of columns that contain
    ingridients and their amounts and units (extracted entities)
    it then combines the entities to a single column of the full recipe ingridients formated  as sentences
    the entities are after units and amounts conversion
    '''
    # Apply the function row by row, passing the column names
    for column in ingredients_columns:
        df[column] = df.apply(formatted_ingrediants, axis=1, column=column)
        df.drop([f'{column}_ingredients',f'{column}_converted'], axis=1, inplace=True)#drop the columns that are no longer needed
    # append the diffrent ingridient columns (steps) to a single column of the full recipe ingridients
    for i in df.index:
        row = df.loc[i][ingredients_columns].copy()
        df.loc[i,'ingredients'] = ' '.join([sentence for sentence in row[~row.isnull()]])
    df.drop(ingredients_columns, axis=1, inplace=True)
    return df  