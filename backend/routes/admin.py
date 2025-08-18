from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from backend import crud, database, models,schemas
from backend.config import templates
from pydantic import ValidationError
from typing import Optional, List

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

# Suspendre un adhérent (POST)
@router.post("/delete/{adherent_id}")
async def suspendre_adherent(adherent_id: int, db: Session = Depends(database.get_db)):
    adherent = db.query(models.Adherent).filter(models.Adherent.id == adherent_id).first()
    if not adherent:
        raise HTTPException(status_code=404, detail="Adhérent non trouvé")
    db.delete(adherent)
    db.commit()
    return RedirectResponse(url="/admin/gestion-adherents", status_code=303)

# Modifier un adhérent (exemple : changer le nom ou l'email)
@router.post("/modify/{adherent_id}")
async def modifier_adherent(
    request: Request,
    adherent_id: int,
    nom: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(database.get_db)
):
    adherent = db.query(models.Adherent).filter(models.Adherent.id == adherent_id).first()
    if not adherent:
        raise HTTPException(status_code=404, detail="Adhérent non trouvé")
    
    errors = None
    try:
        # Validation Pydantic
        adherent_data = schemas.AdherentBase(nom=nom, email=email)
        adherent.nom = adherent_data.nom
        adherent.email = adherent_data.email
        db.commit()
        return RedirectResponse(url="/admin/gestion-adherents", status_code=303)
    except ValidationError as e:
        errors = e.errors()
    
    # En cas d'erreur de validation, on renvoie le template avec les erreurs
    adherents = db.query(models.Adherent).all()
    return templates.TemplateResponse(
        "admin/gestion-adherents.html",
        {
            "request": request,   # Important : passer l'objet Request
            "adherents": adherents,
            "errors": errors      # Tu peux afficher ces erreurs dans le template
        }
    )



@router.get("/gestion-livres")
async def gestion_livres(request: Request, db: Session = Depends(database.get_db), search: str = ""):
    livres = crud.get_livres(db, search)
    return templates.TemplateResponse(
        "admin/gestion-livres.html",
        {"request": request, "livres": livres, "search": search}
    )

@router.post("/livres/add")
async def ajouter_livre(
    titre: str = Form(...),
    auteur: str = Form(...),
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
        return {"errors": e.errors()}

    # Création du livre après validation
    livre = models.Livre(**livre_data.model_dump())
    db.add(livre)
    db.commit()
    return RedirectResponse(url="/admin/gestion-livres", status_code=303)

@router.post("/livres/modify/{livre_id}")
async def modifier_livre(
    livre_id: int,
    titre: Optional[str] = Form(None),
    prix: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    image_url: Optional[str] = Form(None),
    stock: Optional[int] = Form(None),
    db: Session = Depends(database.get_db)
):
    livre = crud.get_livre(db, livre_id)
    if not livre:
        raise HTTPException(404, "Livre non trouvé")

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
    return RedirectResponse(url="/admin/gestion-livres", status_code=303)

@router.get("/livres/delete/{livre_id}")
async def supprimer_livre(livre_id: int, db: Session = Depends(database.get_db)):
    livre = crud.get_livre(db, livre_id)
    if not livre:
        raise HTTPException(404, "Livre non trouvé")
    db.delete(livre)
    db.commit()
    return RedirectResponse(url="/admin/gestion-livres", status_code=303)

@router.get("/emprunts")
async def page_emprunts(request: Request, db: Session = Depends(database.get_db)):
    adherents = db.query(models.Adherent).all()
    livres = db.query(models.Livre).all()
    emprunts = db.query(models.Emprunt).all()
    return templates.TemplateResponse("admin/emprunts.html",
        {"request": request, "adherents": adherents, "livres": livres, "emprunts": emprunts})

@router.post("/emprunts")
async def enregistrer_emprunt(
    id_adherent: int = Form(...),
    id_livre: int = Form(...),
    db: Session = Depends(database.get_db)
):
    livre = db.query(models.Livre).filter_by(id=id_livre).first()
    if not livre or livre.stock <= 0:
        raise HTTPException(400, "Livre indisponible")
    # créer emprunt + maj stock
    from datetime import date, timedelta
    e = models.Emprunt(
        id_adherent=id_adherent,
        id_livre=id_livre,
        date_emprunt=date.today(),
        date_retour_prevue=date.today() + timedelta(days=14),
    )
    db.add(e)
    livre.stock -= 1
    db.commit()
    return RedirectResponse(url="/admin/emprunts", status_code=303)

@router.post("/retours")
async def enregistrer_retour(
    emprunt_id: int = Form(...),
    db: Session = Depends(database.get_db)
):
    from datetime import date
    e = db.query(models.Emprunt).filter_by(id=emprunt_id).first()
    if not e or e.date_retour_effectif:
        raise HTTPException(400, "Emprunt introuvable ou déjà retourné")
    e.date_retour_effectif = date.today()
    livre = db.query(models.Livre).filter_by(id=e.id_livre).first()
    livre.stock += 1
    db.commit()
    return RedirectResponse(url="/admin/emprunts", status_code=303)