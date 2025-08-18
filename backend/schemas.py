from pydantic import BaseModel, EmailStr, Field,field_validator
from typing import Optional, List
from datetime import date
import re

# Adherent (utilisateur)
class AdherentBase(BaseModel):
    nom: str = Field(..., example="Ahmed Benali")
    email: EmailStr

    @field_validator("nom")
    def nom_sans_chiffres(cls, v):
        if re.search(r'\d', v):
            raise ValueError("Le nom ne peut pas contenir de chiffres")
        return v

class AdherentCreate(AdherentBase):
    password: str = Field(..., min_length=6)

class AdherentOut(AdherentBase):
    id: int
    role: str= "adherent"   #par defaut
    date_inscription: Optional[date]

    class Config:
        from_attributes=True


# Livre
class LivreBase(BaseModel):
    titre: str = Field(..., min_length=1)
    prix: float = Field(0, ge=0)
    description: str = ""
    image_url: str = ""
    stock: int = Field(..., ge=0)
    rating: int = 0
    
class LivreOut(LivreBase):
    id: int

    class Config:
        from_attributes=True


# Réservation
class ReservationBase(BaseModel):
    id_adherent: int
    id_livre: int

class ReservationOut(ReservationBase):
    id: int
    date_reservation: Optional[date]
    statut: Optional[str]

    class Config:
        from_attributes=True


# Emprunt
class EmpruntBase(BaseModel):
    id_adherent: int
    id_livre: int
    date_emprunt: Optional[date]
    date_retour_prevue: date

class EmpruntOut(EmpruntBase):
    id: int
    date_retour_effectif: Optional[date]

    class Config:
        from_attributes=True