from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str

    model_config = ConfigDict(from_attributes=True)


class UsuarioAdminSchema(BaseModel):
    nome: str
    email: str
    senha: str
    admin: bool = False

    model_config = ConfigDict(from_attributes=True)


class PedidoSchema(BaseModel):
    id_usuario: int

    model_config = ConfigDict(from_attributes=True)


class ItemPedidoSchema(BaseModel):
    quantidade: int
    sabor: str
    tamanho: str
    preco_unitario: float

    model_config = ConfigDict(from_attributes=True)


class ResponsePedidoSchema(BaseModel):
    id: int
    status: str
    usuario: int
    preco: float
    itens: List[ItemPedidoSchema]

    model_config = ConfigDict(from_attributes=True)


class LoginSchema(BaseModel):
    email: str
    senha: str

    model_config = ConfigDict(from_attributes=True)