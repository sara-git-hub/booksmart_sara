from sqlalchemy.orm import Session
from backend import crud, database

# Créer une session avec la DB
db: Session = next(database.get_db())

# Remplace ces valeurs par ce que tu veux pour ton admin
nom_admin = "Administrateur"
email_admin = "admin@booksmart.com"
password_admin = "MotDePasse123"

# Créer l'admin
admin = crud.create_admin(db, nom_admin, email_admin, password_admin)

print(f"Admin créé avec succès : {admin.nom} ({admin.email})")