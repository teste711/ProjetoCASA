"""Categorias (limite 3) com seus botões (limite 5). Imagens/áudios ficam no Firebase Storage; aqui só as URLs."""
import uuid

from fastapi import APIRouter, Depends

from ..config import settings
from ..deps import erro, get_db, usuario_atual
from ..schemas import BotaoIn, BotaoUpdate, CategoriaIn
from ..util import bump_dispositivos, slugify

router = APIRouter(tags=["Categorias e botões"])


def _col(db, uid):
    return db.collection("usuarios").document(uid).collection("categorias")


def _carregar(db, uid, cid):
    ref = _col(db, uid).document(cid)
    snap = ref.get()
    if not snap.exists:
        raise erro(404, "nao_encontrado", "Categoria não encontrada.")
    return ref, {"id": cid, **snap.to_dict()}


def _todas(db, uid):
    itens = [{"id": s.id, **s.to_dict()} for s in _col(db, uid).stream()]
    return sorted(itens, key=lambda c: c.get("ordem", 0))


@router.get("/categorias")
def listar(busca: str | None = None, u=Depends(usuario_atual), db=Depends(get_db)):
    itens = _todas(db, u["uid"])
    if busca:
        itens = [c for c in itens if busca.strip().lower() in c["nome"].lower()]
    return itens


@router.post("/categorias", status_code=201)
def criar(dados: CategoriaIn, u=Depends(usuario_atual), db=Depends(get_db)):
    existentes = _todas(db, u["uid"])
    if len(existentes) >= settings.max_categorias:
        raise erro(409, "limite_categorias", f"Você pode ter no máximo {settings.max_categorias} categorias.")
    if any(c["nome"].lower() == dados.nome.lower() for c in existentes):
        raise erro(409, "categoria_duplicada", "Já existe uma categoria com esse nome.")
    ref = _col(db, u["uid"]).document(uuid.uuid4().hex[:12])
    doc = {"nome": dados.nome, "slug": slugify(dados.nome), "cor": dados.cor, "ordem": len(existentes), "botoes": []}
    ref.set(doc)
    bump_dispositivos(db, u["uid"])
    return {"id": ref.id, **doc}


@router.patch("/categorias/{cid}")
def renomear(cid: str, dados: CategoriaIn, u=Depends(usuario_atual), db=Depends(get_db)):
    ref, cat = _carregar(db, u["uid"], cid)
    if any(c["id"] != cid and c["nome"].lower() == dados.nome.lower() for c in _todas(db, u["uid"])):
        raise erro(409, "categoria_duplicada", "Já existe uma categoria com esse nome.")
    ref.update({"nome": dados.nome, "slug": slugify(dados.nome), "cor": dados.cor})
    bump_dispositivos(db, u["uid"])
    return {"id": cid, **ref.get().to_dict()}


@router.delete("/categorias/{cid}", status_code=204)
def excluir(cid: str, u=Depends(usuario_atual), db=Depends(get_db)):
    ref, _ = _carregar(db, u["uid"], cid)
    ref.delete()
    bump_dispositivos(db, u["uid"])


@router.post("/categorias/{cid}/botoes", status_code=201)
def criar_botao(cid: str, dados: BotaoIn, u=Depends(usuario_atual), db=Depends(get_db)):
    ref, cat = _carregar(db, u["uid"], cid)
    botoes = cat.get("botoes", [])
    if len(botoes) >= settings.max_botoes_por_categoria:
        raise erro(409, "limite_botoes", f"Cada categoria comporta no máximo {settings.max_botoes_por_categoria} botões.")
    botao = {"id": uuid.uuid4().hex[:12], **dados.model_dump(), "ordem": len(botoes)}
    botao["significado"] = botao["significado"] or botao["rotulo"]
    ref.update({"botoes": botoes + [botao]})
    bump_dispositivos(db, u["uid"])
    return botao


@router.patch("/categorias/{cid}/botoes/{bid}")
def editar_botao(cid: str, bid: str, dados: BotaoUpdate, u=Depends(usuario_atual), db=Depends(get_db)):
    ref, cat = _carregar(db, u["uid"], cid)
    botoes = cat.get("botoes", [])
    b = next((x for x in botoes if x["id"] == bid), None)
    if not b:
        raise erro(404, "nao_encontrado", "Botão não encontrado.")
    b.update(dados.model_dump(exclude_unset=True))
    ref.update({"botoes": botoes})
    bump_dispositivos(db, u["uid"])
    return b


@router.delete("/categorias/{cid}/botoes/{bid}", status_code=204)
def excluir_botao(cid: str, bid: str, u=Depends(usuario_atual), db=Depends(get_db)):
    ref, cat = _carregar(db, u["uid"], cid)
    restantes = [b for b in cat.get("botoes", []) if b["id"] != bid]
    if len(restantes) == len(cat.get("botoes", [])):
        raise erro(404, "nao_encontrado", "Botão não encontrado.")
    ref.update({"botoes": restantes})
    bump_dispositivos(db, u["uid"])
