from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from backend import database, models
from backend.config import templates
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from backend.recommender.recommender import preprocess_text_func


router = APIRouter(prefix="/api", tags=["recommandations"])

# Charger le modèle TF-IDF et la matrice
vectorizer = joblib.load(r"C:\Users\lenovo\Documents\BookSmart_Sara\backend\recommender\tfidf_vectorizer.joblib")
cosine_sim = joblib.load(r"C:\Users\lenovo\Documents\BookSmart_Sara\backend\recommender\cosine_similarity_matrix.joblib")
tfidf_matrix = joblib.load(r"C:\Users\lenovo\Documents\BookSmart_Sara\backend\recommender\tfidf_matrix.joblib")


# Page GET : formulaire de saisie
@router.get("/recommander-par-description")
async def get_livres_route(request: Request):
    return templates.TemplateResponse(
        "recommandation-par-description.html",
        {"request": request, "suggestions": [], "description": ""}
    )



@router.post("/recommander-par-description", response_class=HTMLResponse)
async def recommander_par_description(
    request: Request,
    description: str = Form(...),
    db: Session = Depends(database.get_db)
):
    # Transformer la description saisie
    description=preprocess_text_func(description)
    desc_vec = vectorizer.transform([description])

    # Calculer la similarité avec tous les livres
    similarities = cosine_similarity(desc_vec, tfidf_matrix).flatten()

    # Top 5 indices
    top_idx = similarities.argsort()[::-1][:5]

    # Récupérer les livres correspondants depuis la DB
    livres = db.query(models.Livre).all()
    suggestions = [livres[i] for i in top_idx]

    return templates.TemplateResponse("recommandation-par-description.html", {
        "request": request,
        "suggestions": suggestions,
        "description": description
    })
