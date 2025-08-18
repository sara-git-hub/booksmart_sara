import pandas as pd
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles


from backend.utils import clean_all
from backend.scraping.scrap_books_toscrape import BooksToScraper
from backend.recommender.recommender import modele_recommandation
from backend.database import engine, Base
from backend import models
from backend.routes import admin, livres, recommandations, reservations, stats, users
from backend.config import SECRET_KEY, templates


# Création de l'application FastAPI
app = FastAPI()

# Ajouter le middleware de session
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


# Création de la base de données et des tables si elles n'existent pas
Base.metadata.create_all(bind=engine)

# Servir les fichiers statiques
#app.mount("/static", StaticFiles(directory="static"), name="static")

# Vérifier si la table "livres" contient déjà des livres
with Session(engine) as session:
    livre_count = session.query(models.Livre).count()

if livre_count == 0:
    print("Table livres vide, lancement du scraping...")
    
    # Scraping
    scraper = BooksToScraper(
        driver_path=r'C:\Users\lenovo\Documents\BookSmart_Sara\backend\chromedriver.exe',
        headless=True
    )
    df = scraper.scrape_books()
    print(f"Scraping terminé. Nombre de livres récupérés : {len(df)}")
    
    # Sauvegarde des CSV (brut et nettoyé)
    df.to_csv(r'C:\Users\lenovo\Documents\BookSmart_Sara\data\livres_bruts.csv', index=False)
    
    # Nettoyage des données
    df_cleaned = clean_all(df)
    df_cleaned.to_csv(r'C:\Users\lenovo\Documents\BookSmart_Sara\data\livres_nettoyes.csv', index=False)
    
    # Charger le modèle de recommandation
    modele_recommandation(df_cleaned)
    
    # Insertion dans la base de données
    df_cleaned.to_sql('livres', con=engine, if_exists='append', index=False)
    print("Insertion des livres terminée.")
else:
    print(f"La table livres contient déjà {livre_count} livres. Scraping et insertion ignorés.")

# Inclusion du routeur des utilisateurs
app.include_router(users.router)

#inclusion du routeur des livres
app.include_router(livres.router)

# Inclusion du routeur des réservations
app.include_router(reservations.router)

# Inclusion du routeur des recommandations
app.include_router(recommandations.router)

# Inclusion du routeur des statistiques
app.include_router(stats.router)

# Inclusion du routeur d'administration
app.include_router(admin.router)    

# Route de test
@app.get("/")
async def root():
    return {"message": "API BookSmart fonctionne !"}
