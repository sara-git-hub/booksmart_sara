from sqlalchemy import Column, Integer, String, Text, Date, Boolean, ForeignKey, TIMESTAMP,Float
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime


class Adherent(Base):
    __tablename__ = "adherents"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password = Column(Text, nullable=False)
    role = Column(String(50), default="adherent")
    date_inscription = Column(TIMESTAMP, default=datetime.now)

    emprunts = relationship("Emprunt", back_populates="adherent")
    reservations = relationship("Reservation", back_populates="adherent")
    historique = relationship("HistoriqueEmprunt", back_populates="adherent")
    notifications = relationship("Notification", back_populates="adherent")


class Livre(Base):
    __tablename__ = "livres"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    prix = Column(Float, nullable=False)
    description = Column(Text)
    image_url = Column(Text)
    stock = Column(Integer, default=1)
    rating = Column(Integer)

    emprunts = relationship("Emprunt", back_populates="livre")
    reservations = relationship("Reservation", back_populates="livre")
    historique = relationship("HistoriqueEmprunt", back_populates="livre")


class Emprunt(Base):
    __tablename__ = "emprunts"

    id = Column(Integer, primary_key=True, index=True)
    id_adherent = Column(Integer, ForeignKey("adherents.id", ondelete="CASCADE"))
    id_livre = Column(Integer, ForeignKey("livres.id", ondelete="CASCADE"))
    date_emprunt = Column(Date, default=datetime.utcnow)
    date_retour_prevue = Column(Date, nullable=False)
    date_retour_effectif = Column(Date, nullable=True)

    adherent = relationship("Adherent", back_populates="emprunts")
    livre = relationship("Livre", back_populates="emprunts")


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    id_adherent = Column(Integer, ForeignKey("adherents.id", ondelete="CASCADE"))
    id_livre = Column(Integer, ForeignKey("livres.id", ondelete="CASCADE"))
    date_reservation = Column(Date, default=datetime.now)
    statut = Column(String(50), default="en_attente")

    adherent = relationship("Adherent", back_populates="reservations")
    livre = relationship("Livre", back_populates="reservations")


class HistoriqueEmprunt(Base):
    __tablename__ = "historique_emprunts"

    id = Column(Integer, primary_key=True, index=True)
    id_adherent = Column(Integer, ForeignKey("adherents.id", ondelete="CASCADE"))
    id_livre = Column(Integer, ForeignKey("livres.id", ondelete="CASCADE"))
    note = Column(Integer)
    date_emprunt = Column(Date, default=datetime.now)

    adherent = relationship("Adherent", back_populates="historique")
    livre = relationship("Livre", back_populates="historique")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    id_adherent = Column(Integer, ForeignKey("adherents.id", ondelete="CASCADE"))
    message = Column(Text, nullable=False)
    date = Column(TIMESTAMP, default=datetime.utcnow)
    lu = Column(Boolean, default=False)

    adherent = relationship("Adherent", back_populates="notifications")