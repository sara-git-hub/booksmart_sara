from fastapi import APIRouter, Depends, HTTPException, status, Response,Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime
from backend import schemas, crud, database,models
from backend.config import templates

# Routeur pour les utilisateurs
router = APIRouter(
    prefix="/api",
    tags=["users"])

# Route pour afficher le formulaire d'enregistrement
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("inscription.html", {"request": request})

# Route pour soumettre le formulaire d'enregistrement
@router.post("/register")
async def register_submit(
    request: Request,
    nom: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    try:
        # Vérifier que les mots de passe correspondent
        if password != confirm_password:
            return templates.TemplateResponse("inscription.html", {
                "request": request,
                "error": "Les mots de passe ne correspondent pas."
            })
        
        # Validation via Pydantic
        adherent_data = schemas.AdherentCreate(nom=nom, email=email, password=password)
        
        # Vérification de l'unicité du nom et de l'email"
        if crud.get_adherent_by_name(db, adherent_data.nom):
            raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris.")
        if crud.get_adherent_by_email(db, adherent_data.email):
            raise HTTPException(status_code=400, detail=("email déjà utilisé."))
        
        # Créer utilisateur
        crud.create_adherent(db, adherent_data)
        
        return templates.TemplateResponse("inscription.html", {
            "request": request,
            "success": "Compte créé avec succès !"
        })
        
    except Exception as e:
        return templates.TemplateResponse("inscription.html", {
            "request": request,
            "error": str(e)
        })


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Route pour soumettre le formulaire de connexion des utilisateurs
@router.post("/login")
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    try:
        # Récupérer l'utilisateur par email
        user = crud.get_adherent_by_email(db, email)
        if not user:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Identifiants invalides."
           })
        
        # Vérifier le mot de passe
        if not crud.verify_password(password, user.password):
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "Identifiants invalides."
            })
        
        # Stocker l'utilisateur en session
        request.session["user_id"] = user.id
        request.session["user_nom"] = user.nom
        request.session["user_role"] = user.role
        
        # Redirection selon le rôle
        if user.role == "admin":
            return RedirectResponse(url="/admin/gestion-adherents", status_code=302)
        else:
            return RedirectResponse(url="/api/home", status_code=302)
        
    except Exception as e:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": f"Erreur: {str(e)}"
        })  
    
# Route pour la déconnexion
@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/api/login?message=deconnecte", status_code=303)

@router.get("/home")
def home(request: Request, db: Session = Depends(database.get_db)):
    # Récupérer l'ID de l'utilisateur depuis la session
    user_id = request.session.get("user_id")
    user = None

    if user_id:
        user = db.query(models.Adherent).filter(models.Adherent.id == user_id).first()

    # Récupérer tous les livres
    livres = db.query(models.Livre).all()

    return templates.TemplateResponse(
        "home.html",
        {"request": request, "livres": livres, "user": user}
    )

@router.get("/mes-emprunts")
async def mes_emprunts(request: Request, db: Session = Depends(database.get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Utilisateur non connecté")

    emprunts = db.query(models.Emprunt).filter_by(id_adherent=user_id).all()
    return {"emprunts": [
        {
            "titre": e.livre.titre,
            "date_emprunt": e.date_emprunt.strftime("%d/%m/%Y"),
            "date_retour_prevue": e.date_retour_prevue.strftime("%d/%m/%Y"),
            "en_retard": datetime.utcnow() > e.date_retour_prevue
        } for e in emprunts
    ]}

@router.get("/profil")
async def profil(request: Request, db: Session = Depends(database.get_db)):
    user = crud.get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/api/login", status_code=303)

    emprunts = db.query(models.Emprunt).filter_by(id_adherent=user.id).all()
    return templates.TemplateResponse("profil.html", {"request": request, "user": user, "emprunts": emprunts})


