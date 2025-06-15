from app.db.session import Base, engine
from app.db.models import Todo

print("Création des tables…")
Base.metadata.create_all(bind=engine)
print("✅ Tables créées avec succès.")
