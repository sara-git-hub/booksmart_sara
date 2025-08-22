from fastapi import Form, Depends, APIRouter, Request, HTTPException
from sqlalchemy.orm import Session
from backend import database, crud, models
from backend.config import templates

# Routeur pour les reservations
router = APIRouter(
    prefix="/api",
    tags=["reservations"])

# Route pour créer une reservation adherent
@router.post("/reservations")
async def create_reservation(
    request: Request,
    id_livre: int = Form(...),
    db: Session = Depends(database.get_db)
):
    # Récupérer le livre
    livre = db.query(models.Livre).filter_by(id=id_livre).first()
    if not livre:
        return templates.TemplateResponse(
            "home.html",
            {"request": request, "error": "Livre introuvable.", "success": None, "user": crud.get_current_user(request, db)}
        )

    # Récupérer l'utilisateur depuis la session
    user = crud.get_current_user(request, db)
    if not user:
        return templates.TemplateResponse(
            "livre.html",
            {"request": request, "error": "Veuillez vous connecter pour réserver.", "success": None, "livre": livre, "user": None}
        )

    id_adherent = user.id

    # Vérifier si le livre est déjà réservé par cet adhérent
    existing_reservation = db.query(models.Reservation).filter_by(
        id_adherent=id_adherent, id_livre=id_livre
    ).first()
    if existing_reservation:
        return templates.TemplateResponse(
            "livre.html",
            {"request": request, "error": "Vous avez déjà réservé ce livre.", "success": None, "livre": livre, "user": user}
        )
    
    # Vérifier si l’adhérent a déjà emprunté ce livre et ne l’a pas encore rendu
    emprunt_existant = (
        db.query(models.Emprunt)
        .filter(
            models.Emprunt.id_adherent == id_adherent,
            models.Emprunt.id_livre == id_livre,
            models.Emprunt.date_retour_effectif.is_(None)  # pas encore rendu
        )
        .first()
    )
    if emprunt_existant:
        return templates.TemplateResponse(
            "livre.html",
            {
                "request": request,
                "error": "Vous avez déjà ce livre en cours d’emprunt.",
                "success": None,
                "livre": livre,
                "user": user
            }
        )

    # Vérifier la disponibilité
    if livre.stock <= 0:
        return templates.TemplateResponse(
            "livre.html",
            {"request": request, "error": "Livre non disponible.", "success": None, "livre": livre, "user": user}
        )

    # Créer la réservation
    reservation = models.Reservation(id_adherent=id_adherent, id_livre=id_livre)
    db.add(reservation)
    livre.stock -= 1
    db.commit()

    return templates.TemplateResponse(
        "livre.html",
        {"request": request, "success": "Réservation effectuée avec succès !", "error": None, "livre": livre, "user": user}
    )