from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load pre-trained SBERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

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

def compute_similarity_matrix(data_sets, weights):
    """Compute a similarity matrix for multiple recipe datasets."""
    # Generate embeddings for each dataset
    embeddings = [compute_data_embedding(data, model) for data in data_sets]
    
    # Initialize the similarity matrix
    num_recipes = len(data_sets)
    similarity_matrix = np.zeros((num_recipes, num_recipes))
    
    # Compute pairwise weighted similarity for all pairs of recipes
    for i in range(num_recipes):
        for j in range(num_recipes):
            similarity_matrix[i][j] = compute_weighted_similarity(embeddings[i], embeddings[j], weights)
    
    return similarity_matrix

