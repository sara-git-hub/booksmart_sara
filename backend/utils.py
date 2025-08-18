import pandas as pd
import numpy as np  
import re


# Nettoyage des données
def clean_all(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Nettoyage texte
    def nettoyer_texte(txt):
        txt = re.sub(r'[^A-Za-z0-9À-ÿ\s]', '', str(txt))
        txt = re.sub(r'\s+', ' ', txt)
        return txt.strip()

    # Prix en float
    def prix_float(txt):
        txt = str(txt).replace('£', '').replace('$', '').replace('€', '').strip()
        try:
            return float(txt)
        except ValueError:
            return np.nan

    # Disponibilité en int
    def int_disponibilite(txt):
        match = re.search(r'\d+', str(txt))
        if match:
            nb_dispo = int(match.group())
            return nb_dispo if nb_dispo > 0 else np.nan
        return np.nan

    # Rating en int
    def int_rating(txt):
        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        return rating_map.get(str(txt), np.nan)

    # traitements
    if 'description' in df.columns:
        df['description'] = df['description'].apply(nettoyer_texte)
        mask = df['description'].str.lower() == "no description available"
        df.loc[mask, 'description'] = df['titre']

    if 'prix' in df.columns:
        df['prix'] = df['prix'].apply(prix_float)

    if 'stock' in df.columns:
        df['stock'] = df['stock'].apply(int_disponibilite)

    if 'rating' in df.columns:
        df['rating'] = df['rating'].apply(int_rating)

    return df
