from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Load pre-trained SBERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

def prepare_data(df):
    '''Prepare the data for the similarity computation by combining the ingredients, title, instructions 
    of the recipe into a single list'''
    data = []
    for i in df.index:
        data.append([df.loc[i,'ingredients'],   # ingredients
                     df.loc[i,'title'],         # title
                     df.loc[i,'instructions'],         # instructions
                     ])
    return data
def compute_sentence_embedding(sentence, model):
    """Generate embeddings for a single sentence."""
    embedding = model.encode([sentence])[0]
    return embedding

def compute_data_embedding(data, model):
    """Generate embeddings for a list of sentences (data)."""
    embedding_data = []
    for sentence in data:
        embedding = compute_sentence_embedding(sentence, model)
        embedding_data.append(embedding)
    return embedding_data

def compute_cosine_similarity(embedding_sentence_1, embedding_sentence_2):
    """Compute cosine similarity between two embeddings."""
    def sigmoid(z):
        return 1 / (1 + np.exp(-z))  # Normalize similarity to range between 0 and 1
    
    similarity = cosine_similarity([embedding_sentence_1], [embedding_sentence_2])[0][0]
    return similarity
    # return sigmoid(similarity - 0.5)  # Shift cosine similarity to center around 0.5

def compute_weighted_similarity(embedding_data_1, embedding_data_2, weights):
    """Compute weighted similarity between two sets of embeddings."""
    weighted_similarity = 0
    for embedding_sentence_1, embedding_sentence_2, weight in zip(embedding_data_1, embedding_data_2, weights):
        weighted_similarity += weight * compute_cosine_similarity(embedding_sentence_1, embedding_sentence_2)
    return weighted_similarity

def compute_similarity_matrix(recipes, weights,index = None):
    """Compute a similarity matrix for multiple recipe datasets."""
    # Generate embeddings for each recipe dataset
    embeddings = [compute_data_embedding(recipe, model) for recipe in recipes]
    

    # Compute pairwise weighted similarity for all pairs of recipes
    num_recipes = len(recipes)
    similarity_matrix = -np.ones((num_recipes, num_recipes))
    for i in range(num_recipes):
        for j in range(i, num_recipes):  # Start from i to avoid redundant pairs
            similarity = compute_weighted_similarity(embeddings[i], embeddings[j], weights)
            similarity_matrix[i][j] = similarity
            similarity_matrix[j][i] = similarity  # Ensure symmetry
    index = index if index is not None else range(num_recipes)
    similarity_matrix = pd.DataFrame(similarity_matrix, index=index, columns=index)
    return similarity_matrix

def min_max_indexes_symetric_df(df):
    # Mask the lower triangle and diagonal to avoid redundant pairs to find max (drop the diagonal)
    upper_triangle_df = pd.DataFrame(np.triu(df.values, k=1), index=df.index, columns=df.columns)
    
    # Get the indices of the min and max values in the upper triangle
    min_idx = df.stack().idxmin()  # Returns (row, column) of min value
    max_idx = upper_triangle_df.stack().idxmax()  # Returns (row, column) of max value

    # the value of the min and max values
    min_value = df.loc[min_idx[0], min_idx[1]]
    max_value = df.loc[max_idx[0], max_idx[1]]
    return min_idx, max_idx ,min_value,max_value