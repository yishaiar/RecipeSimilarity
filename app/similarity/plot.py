import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Step 1: Generate a random matrix of size 1000x1000 with values between 0 and 1
def generate_dummy_matrix(size):
    similarity_matrix = np.random.rand(size, size)
    similarity_matrix = (similarity_matrix + similarity_matrix.T) / 2  # Make the matrix symmetric
    np.fill_diagonal(similarity_matrix, 1)  # Set the diagonal to 1
    return similarity_matrix



def plot_heatmap(similarity_matrix, labels=None):
    """Plot a heatmap for the similarity matrix."""

    # Step 1: Create labels (optional, only display a subset of labels)
    labels = [f"Recipe {i+1}" for i in range(len(similarity_matrix))]

    # step 2: limit the labels to a subset to avoid clutter
    subset_size = 50  # Display the first 50 recipes
    subset_labels = labels[:subset_size]
    subset_matrix = similarity_matrix[:subset_size, :subset_size]

    # Step 3: Create the heatmap for a smaller subset of the matrix
    plt.figure(figsize=(15, 12))  # Set the size of the plot

    # Use a smaller portion of the matrix (for example, 50x50)
    sns.heatmap(subset_matrix, annot=False, cmap='YlGnBu', xticklabels=subset_labels, yticklabels=subset_labels, cbar=True)

    # Add labels and title
    plt.title("Recipe Similarity Matrix (Subset of 50 Recipes)")
    plt.xlabel("Recipes")
    plt.ylabel("Recipes")

    # Show the plot
    plt.show()
    
