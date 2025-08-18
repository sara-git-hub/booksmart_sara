from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend import database, models,crud
from backend.config import templates
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/admin", tags=["stats"],dependencies=[Depends(crud.admin_required)])

@router.get("/statistiques")
async def page_stats(request: Request):
    return templates.TemplateResponse("admin/statistiques.html", {"request": request})

@router.get("/statistiques/data")
async def stats_data(db: Session = Depends(database.get_db)):
    # Top 5 livres les plus empruntés
    top = (db.query(models.Livre.titre, func.count(models.Emprunt.id).label("nb"))
             .join(models.Emprunt, models.Emprunt.id_livre == models.Livre.id)
             .group_by(models.Livre.id).order_by(func.count(models.Emprunt.id).desc()).limit(5).all())

    # Taux de disponibilité global (sum stock / count livres)
    total_livres = db.query(func.count(models.Livre.id)).scalar() or 0
    livres_disponibles = db.query(func.count(models.Livre.id)).filter(models.Livre.stock > 0).scalar() or 0
    taux_dispo = (livres_disponibles / total_livres) if total_livres else 0

    # Nombre de retards (retour_effectif null et date_retour_prevue < today)
    from datetime import date
    retards = db.query(models.Emprunt).filter(
        models.Emprunt.date_retour_effectif == None,
        models.Emprunt.date_retour_prevue < date.today()
    ).count()

    return JSONResponse({
        "top": [{"titre": t[0], "nb": t[1]} for t in top],
        "taux_dispo": taux_dispo,
        "retards": retards
    })
