from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from backend import crud, database, models,schemas
from backend.config import templates
from pydantic import ValidationError

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
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
async def gestion_livres(request: Request, db: Session = Depends(database.get_db)):
    livres = db.query(models.Livre).all()
    return templates.TemplateResponse("admin/gestion-livres.html", {"request": request, "livres": livres})

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
    livre = models.Livre(
        titre=titre,
        auteur=auteur,
        prix=prix,
        description=description,
        image_url=image_url,
        stock=stock
    )
    db.add(livre)
    db.commit()
    return RedirectResponse(url="/admin/gestion-livres", status_code=303)

@router.post("/livres/modify/{livre_id}")
async def modifier_livre(
    livre_id: int,
    titre: str = Form(...),
    auteur: str = Form(...),
    prix: float = Form(...),
    description: str = Form(""),
    image_url: str = Form(""),
    stock: int = Form(...),
    db: Session = Depends(database.get_db)
):
    livre = db.query(models.Livre).filter(models.Livre.id == livre_id).first()
    if not livre:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    
    livre.titre = titre
    livre.auteur = auteur
    livre.prix = prix
    livre.description = description
    livre.image_url = image_url
    livre.stock = stock
    db.commit()
    return RedirectResponse(url="/admin/gestion-livres", status_code=303)

@router.get("/livres/delete/{livre_id}")
async def supprimer_livre(livre_id: int, db: Session = Depends(database.get_db)):
    livre = db.query(models.Livre).filter(models.Livre.id == livre_id).first()
    if not livre:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    db.delete(livre)
    db.commit()
    return RedirectResponse(url="/admin/gestion-livres", status_code=303)