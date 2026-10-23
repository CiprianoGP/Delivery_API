from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import ItemPedido, Pedido, Usuario
from schemas import PedidoSchema, ItemPedidoSchema, ResponsePedidoSchema
from dependencies import pegar_sessao, verificar_token
from typing import List

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)])

@order_router.get("/")
async def pedidos():
    return {"mensagem": "Você acessou a rota de pedidos!"}

@order_router.post("/")
async def criar_pedido(pedido_schema: PedidoSchema, session = Depends(pegar_sessao)):
    novo_pedido = Pedido(
        usuario=pedido_schema.id_usuario
    )
    session.add(novo_pedido)
    session.commit()
    session.refresh(novo_pedido)
    return {"mensagem": f"Pedido criado com sucesso! ID do pedido: {novo_pedido.id}"}

@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado!")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=403, detail="Você não tem permissão para cancelar este pedido!")
    pedido.status = "CANCELADO"
    session.commit()
    return {
    "mensagem": f"Pedido número {id_pedido} cancelado com sucesso!",
    "pedido_id": pedido.id,
    "status": pedido.status,
}

@order_router.get("/listar", response_model=List[ResponsePedidoSchema])
async def listar_pedidos(
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    if not usuario.admin:
        raise HTTPException(status_code=403, detail="Você não tem autorização para fazer essa operação!")
    return session.query(Pedido).all()

@order_router.post("/pedido/adicionar_item/{id_pedido}")
async def adicionar_item_pedido(
    id_pedido: int,
    item_pedido_schema: ItemPedidoSchema,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não existente!")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=403, detail="Você não tem permissão para adicionar itens a este pedido!")

    item_pedido = ItemPedido(
        item_pedido_schema.quantidade,
        item_pedido_schema.sabor,
        item_pedido_schema.tamanho,
        item_pedido_schema.preco_unitario,
        id_pedido,   # ligação com o pedido
    )
    session.add(item_pedido)
    session.flush()              # grava o item para o cálculo enxergá-lo
    pedido.calcular_preco()
    session.commit()

    return {
        "mensagem": f"Item adicionado ao pedido {id_pedido} com sucesso!",
        "item_id": item_pedido.id,
        "preco_pedido": pedido.preco,
    }

@order_router.delete("/pedido/remover-item/{id_item_pedido}")
async def remover_item_pedido(
    id_item_pedido: int,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    item_pedido = session.query(ItemPedido).filter(ItemPedido.id == id_item_pedido).first()
    if not item_pedido:
        raise HTTPException(status_code=404, detail="Item no pedido não existente!")

    pedido = session.query(Pedido).filter(Pedido.id == item_pedido.pedido).first()
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=403, detail="Você não tem permissão para remover itens deste pedido!")

    session.delete(item_pedido)
    session.flush()
    pedido.calcular_preco() 
    session.commit()

    return {
        "mensagem": "Item removido com sucesso!",
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido
    }

@order_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(
    id_pedido: int,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado!")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=403, detail="Você não tem permissão para finalizar este pedido!")
    if not pedido.itens:
        raise HTTPException(status_code=400, detail="O pedido não tem itens!")

    pedido.calcular_preco()
    pedido.status = "FINALIZADO"
    session.commit()

    return {
        "mensagem": f"Pedido número {id_pedido} finalizado com sucesso!",
        "pedido_id": pedido.id,
        "status": pedido.status,
        "preco": pedido.preco,
    }

@order_router.get("/pedido/{id_pedido}")
async def visualizar_pedido(
    id_pedido: int,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado!")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=403, detail="Você não tem permissão para ver este pedido!")

    return {
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": ResponsePedidoSchema.model_validate(pedido),
    }

@order_router.get("/listar/pedidos-usuario", response_model=List[ResponsePedidoSchema])
async def listar_pedidos_usuario(
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    return session.query(Pedido).filter(Pedido.usuario == usuario.id).all()