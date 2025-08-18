from sqlalchemy.orm import Session
from backend import models, schemas
from passlib.context import CryptContext
from datetime import datetime
from fastapi import Request, HTTPException, Depends


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --------------------------------------------
# Adhérents
#--------------------------------------------


# Hasher le mot de passe
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Vérifier le mot de passe
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_current_user(request: Request, db: Session) -> "models.Adherent | None":
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(models.Adherent).filter(models.Adherent.id == user_id).first()

# Créer un nouvel adhérent
def create_adherent(db: Session, adherent: schemas.AdherentCreate):
    hashed_pw = hash_password(adherent.password)
    db_adherent = models.Adherent(
        nom=adherent.nom,
        email=adherent.email,
        password=hashed_pw
    )
    db.add(db_adherent)
    print("Création adhérent :", db_adherent.nom, db_adherent.email, db_adherent.password)
    db.commit()
    db.refresh(db_adherent)
    return db_adherent

# Rechercher un adhérent par email
def get_adherent_by_email(db: Session, email: str):
    return db.query(models.Adherent).filter(models.Adherent.email == email).first()

# Rechercher un adhérent par nom
def get_adherent_by_name(db: Session, nom: str):
    return db.query(models.Adherent).filter(models.Adherent.nom == nom).first()

# --------------------------------------------
# livres
#--------------------------------------------

# Récupérer les livres avec recherche
def get_livres(db: Session, search: str = ""):
    if search:
        return db.query(models.Livre).filter(models.Livre.titre.ilike(f"%{search}%")).all()# renvoie les livres correspondant à la recherche
    return db.query(models.Livre).all()# renvoie tous les livres


# Récupérer un livre par titre
def get_livre(db: Session, livre_id: int):
    return db.query(models.Livre).filter(models.Livre.id == livre_id).first()

# Vérifier disponibilité (stock > 0)
def livre_disponible(livre: models.Livre):
    return livre.stock > 0

# Réserver un livre (diminue stock de 1)
def create_reservation(db: Session, livre_id: int, adherent_id: int):
    livre = get_livre(db, livre_id)
    if not livre or not livre_disponible(livre):
        return None  # livre non disponible

    # Créer la réservation
    reservation = models.Reservation(
        adherent_id=adherent_id,
        livre_id=livre_id,
        date_reservation=datetime.now()
    )
    db.add(reservation)

    # Décrémenter le stock
    livre.stock -= 1
    db.commit()
    db.refresh(reservation)
    return reservation

def create_admin(db: Session, nom: str, email: str, password: str):
    hashed_password = pwd_context.hash(password)
    admin = models.Adherent(
        nom=nom,
        email=email,
        password=hashed_password,
        role="admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

def admin_required(request: Request):
    if request.session.get("user_role") != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")