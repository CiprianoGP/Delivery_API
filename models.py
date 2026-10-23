from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy_utils.types import ChoiceType

#cria conexão do seu banco de dados
db = create_engine("sqlite:///banco.db")

#cria a base de dados
Base = declarative_base()

# criar as classes/tabelas do banco
# Usuario
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column("id",Integer, primary_key=True, autoincrement=True)
    nome = Column("nome",String(50))
    email = Column("email",String(50), nullable=False)
    senha = Column("senha",String(50))  
    ativo = Column("ativo",Boolean)
    admin = Column("admin",Boolean, default=False)

    def __init__(self, nome, email, senha, ativo=True, admin=False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin

#Pedido

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", String)
    usuario = Column("usuario", ForeignKey("usuarios.id"))
    preco = Column("preco", Float)
    itens = relationship("ItemPedido", cascade="all, delete")

    def __init__(self, usuario, status="PENDENTE", preco=0.0):
        self.usuario = usuario
        self.preco = preco
        self.status = status

    def calcular_preco(self):
        self.preco = sum(item.preco_unitario * item.quantidade for item in self.itens)
        
# ItensPedido
class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column("id",Integer, primary_key=True, autoincrement=True)
    quantidade = Column("quantidade",Integer)
    sabor = Column("sabor",String(50))
    tamanho = Column("tamanho",String(50))
    preco_unitario = Column("preco_unitario",Float)
    pedido = Column("pedido", ForeignKey("pedidos.id")) 

    def __init__(self, quantidade, sabor, tamanho, preco_unitario, pedido):
        self.quantidade = quantidade
        self.sabor = sabor
        self.tamanho = tamanho
        self.preco_unitario = preco_unitario
        self.pedido = pedido

