import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import re
from nltk.tokenize import word_tokenize
import nltk
from nltk.stem import PorterStemmer
import string

# Téléchargement des ressources NLTK et initialisation des outils de traitement
nltk.download('stopwords', quiet=True)
nltk.download('punkt_tab', quiet=True)
stemmer = PorterStemmer()

def preprocess_text_func(text):

        text_1=str(text)
        text_1=text_1.lower()

        # Tokenisation (décompose le texte en tokens)
        tokens = word_tokenize(text_1)
    
        # Supprimer la ponctuation et les caractères spéciaux
        tokens = [re.sub(f'[{re.escape(string.punctuation)}]', '', token) for token in tokens]
        tokens = [token for token in tokens if token]  # supprimer les tokens vides après suppression ponctuation
    
        # Appliquer le stemming
        stemmed_tokens = [stemmer.stem(token) for token in tokens]

        #Join tolkens
        processed_text_str = ' '.join(stemmed_tokens)
    
        return processed_text_str

def modele_recommandation(df):

    # Extraire la colonne 'description' pour le traitement
    descriptions = df['description']
    
    descriptions_clean=descriptions.apply(preprocess_text_func)

    # TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(descriptions_clean)

    # Calcul de la matrice de similarité cosinus
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Sauvegarder le modèle vectorizer et la matrice de similarité
    joblib.dump(vectorizer, r'C:\Users\lenovo\Documents\BookSmart_Sara\backend\recommender\tfidf_vectorizer.joblib')
    joblib.dump(cosine_sim, r'C:\Users\lenovo\Documents\BookSmart_Sara\backend\recommender\cosine_similarity_matrix.joblib')
    joblib.dump(tfidf_matrix, r'C:\Users\lenovo\Documents\BookSmart_Sara\backend\recommender\tfidf_matrix.joblib')


    print("Modèle et matrice sauvegardés avec succès.")
