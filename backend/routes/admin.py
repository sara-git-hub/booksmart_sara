import pandas as pd
from fastapi import APIRouter, Request, Depends, Form, Query
from sqlalchemy.orm import Session
from backend import crud, database, models,schemas
from backend.config import templates
from pydantic import ValidationError
from typing import Optional
from datetime import date, timedelta
from backend.recommender.recommender import modele_recommandation



router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(crud.admin_required)]
)

# Liste des adhérents
@router.get("/gestion-adherents")
async def gestion_adherents(request: Request, db: Session = Depends(database.get_db)):
    adherents = db.query(models.Adherent).all()
    return templates.TemplateResponse("admin/gestion-adherents.html", {"request": request, "adherents": adherents})


# Suspendre un adhérent
@router.post("/delete/{adherent_id}")
async def suspendre_adherent(request:Request,adherent_id: int, db: Session = Depends(database.get_db)):
    adherents = db.query(models.Adherent).all()
    adherent = db.query(models.Adherent).filter(models.Adherent.id == adherent_id).first()
    if not adherent:
        return templates.TemplateResponse(
            "admin/gestion-adherents.html",
            {
                "request": request,
                "adherents": adherents,
                "error": "Adhérent non trouvé"
            }
        )
    db.delete(adherent)
    db.commit()
    adherents = db.query(models.Adherent).all()
    return templates.TemplateResponse(
        "admin/gestion-adherents.html",
        {
            "request": request,
            "adherents": adherents,
            "success": "Adhérent suspendu avec succès !"
        }
    )

# Modifier un adhérent (exemple : changer le nom ou l'email)
@router.post("/modify/{adherent_id}")
async def modifier_adherent(
    request: Request,
    adherent_id: int,
    nom: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(database.get_db)
):
    adherents = db.query(models.Adherent).all()
    adherent = db.query(models.Adherent).filter(models.Adherent.id == adherent_id).first()
    if not adherent:
        return templates.TemplateResponse(
            "admin/gestion-adherents.html",
            {
                "request": request,
                "adherents": adherents,
                "error": "Adhérent non trouvé"
            }
        )
    
    try:
        # Validation Pydantic
        adherent_data = schemas.AdherentBase(nom=nom, email=email)
        adherent.nom = adherent_data.nom
        adherent.email = adherent_data.email
        db.commit()
        # Recharger la liste après modification
        adherents = db.query(models.Adherent).all()
        return templates.TemplateResponse(
            "admin/gestion-adherents.html",
            {
                "request": request,
                "adherents": adherents,
                "success": "Adhérent modifié avec succès !"
            }
        )
    except ValidationError as e:
        errors = e.errors()
        return templates.TemplateResponse(
            "admin/gestion-adherents.html",
            {
                "request": request,
                "adherents": adherents,
                "errors": errors
            }
        )

# Ajouter un adhérent
@router.post("/adherents/add")
async def ajouter_adherent(
    request: Request,
    nom: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    adherents = db.query(models.Adherent).all()

    # 1) Vérifier unicité de l'email
    existing = crud.get_adherent_by_email(db, email)
    if existing:
        return templates.TemplateResponse(
            "admin/gestion-adherents.html",
            {
                "request": request,
                "adherents": adherents,
                "error": "Un adhérent avec cet email existe déjà."
            }
        )

    try:
        #  Validation Pydantic pour nom/email
        data = schemas.AdherentBase(nom=nom, email=email)

        #  Hash du mot de passe
        hashed_password = crud.hash_password(password)

        #  Création et insertion
        nouvel_adherent = models.Adherent(
            nom=data.nom,
            email=data.email,
            password=hashed_password,
        )
        db.add(nouvel_adherent)
        db.commit()
        db.refresh(nouvel_adherent)

        # Recharger la liste
        adherents = db.query(models.Adherent).all()
        return templates.TemplateResponse(
            "admin/gestion-adherents.html",
            {
                "request": request,
                "adherents": adherents,
                "success": "Adhérent ajouté avec succès !"
            }
        )

    except ValidationError as e:
        return templates.TemplateResponse(
            "admin/gestion-adherents.html",
            {
                "request": request,
                "adherents": adherents,
                "errors": e.errors()
            }
        )

@router.get("/gestion-livres")
async def gestion_livres(
    request: Request,
    db: Session = Depends(database.get_db),
    search: str = "",
    id_livre: str = Query("")  # <- récupérer comme string
):
    try:
        id_livre_int: Optional[int] = int(id_livre) if id_livre.strip() else None
    except ValueError:
        id_livre_int = None

    if id_livre_int is not None:
        livres = db.query(models.Livre).filter(models.Livre.id == id_livre_int).all()
    else:
        livres = crud.get_livres(db, search)

    error = None
    if not livres:
        error = "Aucun livre trouvé pour votre recherche."

    return templates.TemplateResponse(
        "admin/gestion-livres.html",
        {
            "request": request,
            "livres": livres,
            "search": search,
            "id_livre": id_livre,
            "error": error
        }
    )


@router.post("/livres/add")
async def ajouter_livre(
    request: Request,
    titre: str = Form(...),
    prix: float = Form(...),
    description: str = Form(""),
    image_url: str = Form(""),
    stock: int = Form(1),
    db: Session = Depends(database.get_db)
):
    try:
        # Validation Pydantic
        livre_data = schemas.LivreBase(
            titre=titre,
            prix=prix,
            description=description,
            image_url=image_url,
            stock=stock
        )
    except ValidationError as e:
        livres = crud.get_livres(db, "")
        return templates.TemplateResponse(
            "admin/gestion-livres.html",
            {
                "request": request,
                "livres": livres,
                "error": "Erreur de validation des données.",
                "errors": e.errors(),
                "success": None
            }
        )

    # Création du livre après validation
    livre = models.Livre(**livre_data.model_dump())
    db.add(livre)
    db.commit()

    # Recalculer le modèle après modification
    livres_df = pd.read_sql_table('livres', con=database.engine)
    modele_recommandation(livres_df)

    livres = crud.get_livres(db, "")
    return templates.TemplateResponse(
        "admin/gestion-livres.html",
        {
            "request": request,
            "livres": livres,
            "success": "Livre ajouté avec succès !",
            "error": None
        }
    )

@router.post("/livres/modify/{livre_id}")
async def modifier_livre(
    request: Request,
    livre_id: int,
    titre: Optional[str] = Form(None),
    prix: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    image_url: Optional[str] = Form(None),
    stock: Optional[int] = Form(None),
    db: Session = Depends(database.get_db)
):
    livre = crud.get_livre(db, livre_id)
    livres = crud.get_livres(db)
    if not livre:
        return templates.TemplateResponse(
            "admin/gestion-livres.html",
            {"request": request, "livres": livres, "error": "Livre non trouvé"}
        )

    if titre is not None:
        livre.titre = titre
    if prix is not None:
        livre.prix = prix
    if description is not None:
        livre.description = description
    if image_url is not None:
        livre.image_url = image_url
    if stock is not None:
        livre.stock = stock

    db.commit()

    # Recalculer le modèle après modification
    livres_df = pd.read_sql_table('livres', con=database.engine)
    modele_recommandation(livres_df)

    # Renvoie le template avec un message de succès
    return templates.TemplateResponse(
        "admin/gestion-livres.html",
        {"request": request, "livres": livres, "success": "Livre modifié avec succès !"}
    )

@router.get("/livres/delete/{livre_id}")
async def supprimer_livre(request: Request, livre_id: int, db: Session = Depends(database.get_db)):
    livres = crud.get_livres(db)  # récupère la liste pour l'affichage
    livre = crud.get_livre(db, livre_id)
    
    if not livre:
        return templates.TemplateResponse(
            "admin/gestion-livres.html",
            {"request": request, "livres": livres, "error": "Livre non trouvé"}
        )

    db.delete(livre)
    db.commit()

    # Recalculer le modèle après modification
    livres_df = pd.read_sql_table('livres', con=database.engine)
    modele_recommandation(livres_df)

    return templates.TemplateResponse(
        "admin/gestion-livres.html",
        {"request": request, "livres": crud.get_livres(db), "success": "Livre supprimé avec succès !"}
    )

# Page de gestion : emprunts + réservations
@router.get("/emprunts")
async def page_emprunts(request: Request, db: Session = Depends(database.get_db)):
    adherents = db.query(models.Adherent).all()
    livres = db.query(models.Livre).all()
    emprunts = db.query(models.Emprunt).all()
    reservations = db.query(models.Reservation).all()
    return templates.TemplateResponse(
        "admin/emprunts.html",
        {
            "request": request,
            "adherents": adherents,
            "livres": livres,
            "emprunts": emprunts,
            "reservations": reservations,
        }
    )

# Route pour enregistrer un emprunt
@router.post("/emprunts")
async def enregistrer_emprunt(
    request: Request,
    id_adherent: int = Form(...),
    id_livre: int = Form(...),
    db: Session = Depends(database.get_db)
):
    adherents = db.query(models.Adherent).all()
    livres = db.query(models.Livre).all()
    emprunts = db.query(models.Emprunt).all()
    reservations = db.query(models.Reservation).all()

    livre = db.query(models.Livre).filter_by(id=id_livre).first()
    if not livre or livre.stock <= 0:
        return templates.TemplateResponse(
            "admin/emprunts.html",
            {
                "request": request,
                "adherents": adherents,
                "livres": livres,
                "emprunts": emprunts,
                "reservations": reservations,
                "error": "Livre indisponible"
            }
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
            "admin/emprunts.html",
            {
                "request": request,
                "adherents": adherents,
                "livres": livres,
                "emprunts": emprunts,
                "reservations": reservations,
                "error": "Cet adhérent a déjà emprunté ce livre et ne l’a pas encore rendu"
            }
        )

    emprunt = models.Emprunt(
        id_adherent=id_adherent,
        id_livre=id_livre,
        date_emprunt=date.today(),
        date_retour_prevue=date.today() + timedelta(days=14),
    )
    db.add(emprunt)
    livre.stock -= 1
    db.commit()

    # Recharger les listes après ajout
    emprunts = db.query(models.Emprunt).all()
    livres = db.query(models.Livre).all()

    return templates.TemplateResponse(
        "admin/emprunts.html",
        {
            "request": request,
            "adherents": adherents,
            "livres": livres,
            "emprunts": emprunts,
            "reservations": reservations,
            "success": "Emprunt enregistré avec succès !"
        }
    )

# Route pour enregistrer un retour
@router.post("/retours")
async def enregistrer_retour(
    request: Request,
    emprunt_id: int = Form(...),
    db: Session = Depends(database.get_db)
):
    adherents = db.query(models.Adherent).all()
    livres = db.query(models.Livre).all()
    emprunts = db.query(models.Emprunt).all()
    reservations = db.query(models.Reservation).all()

    from datetime import date
    e = db.query(models.Emprunt).filter_by(id=emprunt_id).first()
    if not e or e.date_retour_effectif:
        return templates.TemplateResponse(
            "admin/emprunts.html",
            {
                "request": request,
                "adherents": adherents,
                "livres": livres,
                "emprunts": emprunts,
                "reservations": reservations,
                "error": "Emprunt introuvable ou déjà retourné"
            }
        )

    e.date_retour_effectif = date.today()
    livre = db.query(models.Livre).filter_by(id=e.id_livre).first()
    livre.stock += 1
    db.commit()

    # Recharger les listes après action
    emprunts = db.query(models.Emprunt).all()
    livres = db.query(models.Livre).all()

    return templates.TemplateResponse(
        "admin/emprunts.html",
        {
            "request": request,
            "adherents": adherents,
            "livres": livres,
            "emprunts": emprunts,
            "reservations": reservations,
            "success": "Retour enregistré avec succès !"
        }
    )

# Route pour confirmer une réservation
@router.post("/reservations/{reservation_id}/confirmer")
async def confirmer_reservation(request: Request, reservation_id: int, db: Session = Depends(database.get_db)):
    adherents = db.query(models.Adherent).all()
    livres = db.query(models.Livre).all()
    emprunts = db.query(models.Emprunt).all()
    reservations = db.query(models.Reservation).all()

    reservation = db.query(models.Reservation).filter_by(id=reservation_id).first()
    if not reservation:
        return templates.TemplateResponse(
            "admin/emprunts.html",
            {
                "request": request,
                "adherents": adherents,
                "livres": livres,
                "emprunts": emprunts,
                "reservations": reservations,
                "error": "Réservation introuvable"
            }
        )

    livre = db.query(models.Livre).filter_by(id=reservation.id_livre).first()
    if not livre or livre.stock <= 0:
        return templates.TemplateResponse(
            "admin/emprunts.html",
            {
                "request": request,
                "adherents": adherents,
                "livres": livres,
                "emprunts": emprunts,
                "reservations": reservations,
                "error": "Livre indisponible"
            }
        )

    # créer emprunt
    emprunt = models.Emprunt(
        id_adherent=reservation.id_adherent,
        id_livre=reservation.id_livre,
        date_emprunt=date.today(),
        date_retour_prevue=date.today() + timedelta(days=14),
    )
    db.add(emprunt)

    # mettre à jour le stock
    livre.stock -= 1

    # supprimer la réservation
    db.delete(reservation)

    db.commit()

    # recharger les listes après action
    emprunts = db.query(models.Emprunt).all()
    livres = db.query(models.Livre).all()
    reservations = db.query(models.Reservation).all()

    return templates.TemplateResponse(
        "admin/emprunts.html",
        {
            "request": request,
            "adherents": adherents,
            "livres": livres,
            "emprunts": emprunts,
            "reservations": reservations,
            "success": "Réservation confirmée et transformée en emprunt !"
        }
    )

# Route pour supprimer une reservation
@router.post("/reservations/{reservation_id}/supprimer")
async def supprimer_reservation(request: Request, reservation_id: int, db: Session = Depends(database.get_db)):
    adherents = db.query(models.Adherent).all()
    livres = db.query(models.Livre).all()
    emprunts = db.query(models.Emprunt).all()
    reservations = db.query(models.Reservation).all()

    reservation = db.query(models.Reservation).filter_by(id=reservation_id).first()
    if not reservation:
        return templates.TemplateResponse(
            "admin/emprunts.html",
            {
                "request": request,
                "adherents": adherents,
                "livres": livres,
                "emprunts": emprunts,
                "reservations": reservations,
                "error": "Réservation introuvable"
            }
        )

    db.delete(reservation)
    db.commit()

    # recharger les listes après suppression
    emprunts = db.query(models.Emprunt).all()
    reservations = db.query(models.Reservation).all()

    return templates.TemplateResponse(
        "admin/emprunts.html",
        {
            "request": request,
            "adherents": adherents,
            "livres": livres,
            "emprunts": emprunts,
            "reservations": reservations,
            "success": "Réservation supprimée avec succès !"
        }
    )
