from fastapi import Form, Depends, APIRouter, Request, HTTPException
from sqlalchemy.orm import Session
from backend import database, crud, models

# Routeur pour les reservations
router = APIRouter(
    prefix="/api",
    tags=["reservations"])

@router.post("/reservations")
async def create_reservation(
    request: Request,
    id_livre: int = Form(...),  # seul le livre reste en formulaire
    db: Session = Depends(database.get_db)
):
    # Récupérer l'utilisateur depuis la session
    user = crud.get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non connecté")

    id_adherent = user.id

    # Vérifier si le livre est déjà réservé par cet adhérent
    existing_reservation = db.query(models.Reservation).filter_by(
        id_adherent=id_adherent, id_livre=id_livre
    ).first()

    if existing_reservation:
        return {"message": "Vous avez déjà réservé ce livre."}

    # Vérifier la disponibilité
    livre = db.query(models.Livre).filter_by(id=id_livre).first()
    if not livre or livre.stock <= 0:
        return {"message": "Livre non disponible."}

    # Créer la réservation
    reservation = models.Reservation(id_adherent=id_adherent, id_livre=id_livre)
    db.add(reservation)

    # Mettre à jour le stock du livre
    livre.stock -= 1
    db.commit()

    return {"message": "Réservation effectuée avec succès !"}