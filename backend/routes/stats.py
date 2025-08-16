from fastapi import APIRouter, Depends, HTTPException, status, Response,Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend import schemas, crud, database,models
from backend.config import templates

# Routeur pour les statistiques
router = APIRouter(
    prefix="/api",
    tags=["statistiques"])


@router.get("/statistiques")
async def statistiques(request: Request, db: Session = Depends(database.get_db)):
    # 5 livres les plus empruntés
    top_livres = db.query(models.Livre).join(models.Emprunt).group_by(models.Livre.id).order_by(models.func.count(models.Emprunt.id).desc()).limit(5).all()

    # Taux de disponibilité global
    total_livres = db.query(models.Livre).count()
    livres_disponibles = db.query(models.Livre).filter(models.Livre.stock > 0).count()
    taux_dispo = (livres_disponibles / total_livres * 100) if total_livres > 0 else 0

    # Nombre de retards
    retards = db.query(models.Emprunt).filter(models.Emprunt.date_retour < models.Emprunt.date_emprunt).count()  # Exemple simple

    return templates.TemplateResponse("admin/statistiques.html", {
        "request": request,
        "top_livres": top_livres,
        "taux_dispo": taux_dispo,
        "retards": retards
    })