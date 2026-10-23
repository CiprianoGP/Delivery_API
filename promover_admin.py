from sqlalchemy.orm import sessionmaker
from models import db, Usuario

Session = sessionmaker(bind=db)
session = Session()

usuario = session.query(Usuario).filter(Usuario.email == "cipri@gmail.com").first()

if usuario:
    usuario.admin = True
    session.commit()
    print("OK:", usuario.email, "admin =", usuario.admin)
else:
    print("Usuário não encontrado")

session.close()