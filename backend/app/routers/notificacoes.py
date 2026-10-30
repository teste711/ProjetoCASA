"""Sino de notificações (pareamento, bateria baixa)."""
from fastapi import APIRouter, Depends, Query

from ..deps import erro, get_db, usuario_atual

router = APIRouter(prefix="/notificacoes", tags=["Notificações"])


def _col(db, uid):
    return db.collection("usuarios").document(uid).collection("notificacoes")


@router.get("")
def listar(apenas_nao_lidas: bool = False, limite: int = Query(30, ge=1, le=100), u=Depends(usuario_atual), db=Depends(get_db)):
    todas = sorted(({"id": s.id, **s.to_dict()} for s in _col(db, u["uid"]).stream()),
                   key=lambda n: n["criada_em"], reverse=True)
    itens = [n for n in todas if not (apenas_nao_lidas and n["lida"])][:limite]
    return {"nao_lidas": sum(1 for n in todas if not n["lida"]), "itens": itens}


@router.post("/lidas", summary="Marca todas como lidas")
def marcar_todas(u=Depends(usuario_atual), db=Depends(get_db)):
    for s in _col(db, u["uid"]).stream():
        s.reference.update({"lida": True})
    return {"mensagem": "Notificações marcadas como lidas."}


@router.post("/{nid}/lida")
def marcar_lida(nid: str, u=Depends(usuario_atual), db=Depends(get_db)):
    ref = _col(db, u["uid"]).document(nid)
    if not ref.get().exists:
        raise erro(404, "nao_encontrado", "Notificação não encontrada.")
    ref.update({"lida": True})
    return {"id": nid, **ref.get().to_dict()}


@router.delete("", summary="Limpa todas as notificações")
def limpar(u=Depends(usuario_atual), db=Depends(get_db)):
    for s in list(_col(db, u["uid"]).stream()):
        s.reference.delete()
    return {"mensagem": "Notificações removidas."}
