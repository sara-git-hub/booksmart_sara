import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib

def modele_recommandation(df):

    # Extraire la colonne 'description' pour le traitement
    descriptions = df['description']

    # TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(descriptions)

    # Calcul de la matrice de similarité cosinus
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Sauvegarder le modèle vectorizer et la matrice de similarité
    joblib.dump(vectorizer, r'C:\Users\lenovo\Documents\BookSmart_Sara\backend\recommender\tfidf_vectorizer.joblib')
    joblib.dump(cosine_sim, r'C:\Users\lenovo\Documents\BookSmart_Sara\backend\recommender\cosine_similarity_matrix.joblib')

    print("Modèle et matrice sauvegardés avec succès.")
