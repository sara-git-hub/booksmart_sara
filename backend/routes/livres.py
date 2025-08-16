from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from backend import crud, database
from backend.config import templates
from backend import models, schemas

router = APIRouter(prefix="/api", tags=["livres"])

@router.get("/livres")
async def get_livres_route(request: Request, search: str = "", db: Session = Depends(database.get_db)):
    livres = crud.get_livres(db, search)
    user = crud.get_current_user(request, db)  # <- utilisation de la fonction

    return templates.TemplateResponse(
        "home.html",
        {"request": request, "livres": livres, "search": search, "user": user}
    )

@router.get("/livre/{livre_id}")
async def livre_detail(request: Request, livre_id: int, db: Session = Depends(database.get_db)):
    livre = crud.get_livre(db, livre_id)
    if not livre:
        return templates.TemplateResponse(
            "home.html",
            {"request": request, "error": "Livre introuvable"}
        )

    # Récupérer l'utilisateur connecté
    user = crud.get_current_user(request, db)

    return templates.TemplateResponse(
        "livre.html",
        {"request": request, "livre": livre, "user": user}
    )