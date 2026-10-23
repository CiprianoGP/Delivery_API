from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import pegar_sessao, verificar_token, verificar_admin
from models import Usuario
from main import bcrypt_context, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas import UsuarioSchema, LoginSchema, UsuarioAdminSchema
from jose import jwt, ExpiredSignatureError, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter(prefix="/auth", tags=["auth"])

  
def criar_token(id_usuario, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dic_info = {"sub": str(id_usuario), "exp": data_expiracao}
    jwt_codificado = jwt.encode(dic_info, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_codificado


def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return False
    if not bcrypt_context.verify(senha, usuario.senha):
        return False
    return usuario

def cadastrar_usuario(nome: str, email: str, senha: str, admin: bool, session: Session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    if usuario:
        raise HTTPException(status_code=400, detail="Email já cadastrado!")

    senha_criptografada = bcrypt_context.hash(senha)
    novo_usuario = Usuario(nome, email, senha_criptografada)
    novo_usuario.admin = admin
    session.add(novo_usuario)
    session.commit()
    return novo_usuario


@auth_router.post("/criar_conta")
async def criar_conta(
    usuario_schema: UsuarioSchema,
    session: Session = Depends(pegar_sessao),
):
    # Rota pública: admin é SEMPRE False
    novo = cadastrar_usuario(
        usuario_schema.nome, usuario_schema.email, usuario_schema.senha,
        admin=False, session=session,
    )
    return {"mensagem": f"Usuário cadastrado com sucesso: {novo.email}"}


@auth_router.post("/criar_conta_admin")
async def criar_conta_admin(
    usuario_schema: UsuarioAdminSchema,
    session: Session = Depends(pegar_sessao),
    admin_logado: Usuario = Depends(verificar_admin),
):
    # Só chega aqui quem tem token válido E é admin
    novo = cadastrar_usuario(
        usuario_schema.nome, usuario_schema.email, usuario_schema.senha,
        admin=usuario_schema.admin, session=session,
    )
    return {"mensagem": f"Usuário cadastrado com sucesso: {novo.email}", "admin": novo.admin}

@auth_router.post("/login")
async def login(
    login_schema: LoginSchema,
    session: Session = Depends(pegar_sessao),
):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)

    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario não encontrado ou senha incorreta!")

    access_token = criar_token(usuario.id)
    refresh_token = criar_token(usuario.id, duracao_token=timedelta(minutes=1440))  # Expira em 24 horas 
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "usuario_id": usuario.id      
    }

@auth_router.post("/login-form")
async def login_form(
    dados_formulario: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(pegar_sessao), 
):
    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)

    if not usuario:
        raise HTTPException(status_code=400, detail="Usuario não encontrado ou senha incorreta!")

    access_token = criar_token(usuario.id) 
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario_id": usuario.id      
    }

@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario_id": usuario.id,
    }

@auth_router.get("/me")
async def me(usuario: Usuario = Depends(verificar_token)):
    return {"id": usuario.id, "nome": usuario.nome, "email": usuario.email, "admin": usuario.admin}