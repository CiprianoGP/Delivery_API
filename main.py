
import os

from fastapi import FastAPI
from passlib.context import CryptContext 
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI()
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],  # endereço do seu frontend
    allow_methods=["*"],
    allow_headers=["*"],
)





from auth_routes import auth_router
from order_routes import order_router

app.include_router(auth_router)
app.include_router(order_router)

# para rodar o codigo no terminal: python -m uvicorn main:app --reload

# endpoint:
# /ordens

# Rest APIs
# Get -> leitura/pegar
# Post -> enviar/criar
# Put/Patch -> edição/atualizar
# Delete -> deletar/excluir  


