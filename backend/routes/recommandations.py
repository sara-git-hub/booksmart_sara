from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from backend import database, models
from backend.config import templates
import joblib
import numpy as np


router = APIRouter(prefix="/api", tags=["recommandations"])

# Charger le modèle TF-IDF et la matrice
vectorizer = joblib.load(r"C:\Users\lenovo\Documents\BookSmart_Sara\backend\recommender\tfidf_vectorizer.joblib")
cosine_sim = joblib.load(r"C:\Users\lenovo\Documents\BookSmart_Sara\backend\recommender\cosine_similarity_matrix.joblib")

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
    # Vectoriser la description saisie
    desc_vec = vectorizer.transform([description])

    # Calculer similarités avec la matrice sauvegardée
    similarities = cosine_sim.dot(desc_vec.T).toarray().flatten()

    # Obtenir les indices des 5 livres les plus similaires
    top_idx = np.argsort(similarities)[::-1][:5]

    # Récupérer les livres correspondants depuis la DB
    livres = db.query(models.Livre).all()
    suggestions = [livres[i] for i in top_idx]

    return templates.TemplateResponse("recommandation-par-descrition.html", {
        "request": request,
        "suggestions": suggestions,
        "description": description
    })
