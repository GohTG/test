from flask import Flask, request, render_template
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

app = Flask(__name__)

# Load the dataset
def load_csv_dataset(file_path):
    df = pd.read_csv(file_path)
    return df[['instruction', 'intent', 'category', 'response']]

# Preprocess the data
def preprocess_data(df):
    return df[['instruction', 'intent', 'category', 'response']]

# Train a model to retrieve responses based on similarity
def train_response_model(df):
    tfidf_vectorizer = TfidfVectorizer()
    X = tfidf_vectorizer.fit_transform(df['instruction'])
    return tfidf_vectorizer, X, df

# Generate response based on user input with fallback for low similarity and greeting handling
def generate_response(user_input, tfidf_vectorizer, X, df, threshold=0.3):
    # Convert user input to lowercase for easier comparison
    user_input_lower = user_input.lower()

    # Define a regex pattern for detecting greetings
    greeting_pattern = r'\b(hi|hello|hey|howdy|hola|hiya|good\s?morning|good\s?afternoon|good\s?evening|greetings|what\'s\s?up|yo)\b'

    # Check if the user input matches the greeting pattern
    if re.search(greeting_pattern, user_input_lower):
        return "Hello! How can I assist you today?"

    # Handle normal responses based on similarity
    user_input_vector = tfidf_vectorizer.transform([user_input])
    similarities = cosine_similarity(user_input_vector, X)
    
    # Get the most similar response
    most_similar_index = np.argmax(similarities)
    highest_similarity = np.max(similarities)
    
    # If the highest similarity is below the threshold, return a fallback response
    if highest_similarity < threshold:
        return "I'm sorry, I didn't quite understand that. Could you please rephrase your question?"
    
    # Otherwise, return the appropriate response from the dataset
    response = df.iloc[most_similar_index]['response']
    return response

# Load and preprocess the data
file_path = r'C:\Users\jonat\Downloads1\TARUMT\Y2S1\BMCS 2003 Artificial Intelligence\Ai Assignment\Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11 (1).csv'  # Update the path to your CSV file
df = load_csv_dataset(file_path)
df = preprocess_data(df)
tfidf_vectorizer, X, df = train_response_model(df)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['user_input']
        response = generate_response(user_input, tfidf_vectorizer, X, df)
        return render_template('base2.html', user_input=user_input, response=response)
    return render_template('base2.html', user_input='', response='')

if __name__ == "__main__":
    app.run(debug=True)
