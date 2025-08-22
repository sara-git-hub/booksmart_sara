#  📚 Booksmart - Gestion de bibliotheque

BookSmart est une application web développée avec FastAPI, permettant de gérer un catalogue de livres, les emprunts, les réservations et proposant des recommandations basées sur les descriptions des ouvrages (TF-IDF & cosine similarity). Une interface admin permet d'ajouter, modifier ou supprimer des livres, de gerer les adherents et les emprunts.

## ✨Fonctionnalités principales

### Scraping et population initiale
 - Récupération des livres depuis un site (BooksToScraper).

### Nettoyage des données (clean_all).
 - Sauvegarde dans la base de données via SQLAlchemy.

### Gestion des livres (Admin)
 - Ajout, modification, suppression des livres.
 - Recalcul automatique du modèle de recommandation après chaque changement, pour garder les suggestions à jour.

### Réservations & Emprunts
 - Réservation de livres par les adhérents (avec vérification stock disponible).
 - Confirmation ou suppression des réservations via interface admin, transformation en emprunt, gestion des retours.

###  🔮 Recommandation par description
 - Interface utilisateur pour saisir une description.
 - Recherche des livres les plus similaires via un modèle TF-IDF / cosine similarity.

### 🔐 Authentification & rôles
 - Garde-fou admin_required pour les routes administratives.
 - Gestion de session et rôle utilisateur adherent/admin.

### 📊 Statistiques Avancées
 - Tableau de bord
 - Visualisation des tendances

### 🔧 Technologies Clés

**Backend:**
 - FastAPI
 - SQLAlchemy ORM
 - Pydantic (validation)
 - Passlib (hash)

**Frontend:**
 - Jinja2 Templates
 - HTML/CSS/Tailwil/chart.js

**Data:**
 - Selenium (scrapping)
 - PostgreSQL
 - Pandas (prétraitement)

**ML:**
 - TfidfVectorizer
 - cosine_similarity
 - Joblib (sérialisation)


### 📊 Structure du projet

```bash
booksmart/
│
├── backend/
│   ├── main.py                   # Point d'entrée FastAPI
│   ├── database.py               # Connexion PostgreSQL
│   ├── models.py                 # Tables SQLAlchemy
│   ├── schemas.py                # Schémas Pydantic
│   ├── crud.py                   # Fonctions d'accès aux données
│   ├── config.py                 # configuration centralisée
│   ├── scraping/
│   │   └── scrap_books_toscrape.py  # Script Selenium
│   ├── recommender/
│   │   ├── recommender.py        # Modèle TF-IDF + similarité cosinus
│   │   └── model.pkl             # Modèle sauvegardé
│   ├── routes/
│   │   ├── users.py              # Inscription / connexion
│   │   ├── livres.py             # Recherche / consultation / stock
│   │   ├── reservations.py       # Réservations et emprunts
│   │   ├── admin.py              # Gestion admin
│   │   ├── stats.py              # Statistiques
│   │   └── recommandations.py    # Suggestions
│   └── utils.py                  # Fonctions utilitaires
│
├── frontend/
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── inscription.html
│   │   ├── login.html
│   │   ├── livre_detail.html
│   │   ├── livre.html
│   │   ├── profil.html
│   │   ├── recommandation-par-description.html
│   │   ├── admin/
│   │   │   ├── gestion-adherents.html
│   │   │   ├── gestion-livres.html
│   │   │   ├── emprunts.html
│   │   │   ├── statistiques.html
│
├── data/
│   ├── livres_bruts.csv          # Données scrapées
│   ├── livres_nettoyes.csv       # Données nettoyées
│   └── sauvegardes/              # Backups DB
│
├── .env                          # Variables d'environnement (DB, secrets)
├── requirements.txt              # Dépendances Python
├── README.md                     # Documentation projet
└── run.sh                        # Script lancement local