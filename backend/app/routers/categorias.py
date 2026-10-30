"""Categorias (limite 3) com seus botões (limite 5). Imagens/áudios ficam no Firebase Storage; aqui só as URLs."""
import uuid

from fastapi import APIRouter, Depends

from ..config import settings
from ..deps import erro, get_db, usuario_atual
from ..schemas import BotaoIn, BotaoUpdate, CategoriaIn, OrdemIn
from ..util import bump_dispositivos, liberar_midias, slugify

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
    campos = {"nome": dados.nome, "slug": slugify(dados.nome)}
    if "cor" in dados.model_fields_set:      # só altera a cor se ela foi enviada
        campos["cor"] = dados.cor
    ref.update(campos)
    bump_dispositivos(db, u["uid"])
    return {"id": cid, **ref.get().to_dict()}


@router.delete("/categorias/{cid}", status_code=204)
def excluir(cid: str, u=Depends(usuario_atual), db=Depends(get_db)):
    ref, cat = _carregar(db, u["uid"], cid)
    midias = {m for b in cat.get("botoes", []) for m in (b.get("imagem_id"), b.get("audio_id")) if m}
    ref.delete()
    liberar_midias(db, u["uid"], midias)
    bump_dispositivos(db, u["uid"])


def _midia(db, uid: str, mid: str | None, tipo: str) -> dict | None:
    """Confere que a mídia existe, é do usuário e é do tipo certo. Retorna os metadados (ou None)."""
    if mid is None:
        return None
    snap = db.collection("usuarios").document(uid).collection("midias").document(mid).get()
    if not snap.exists:
        raise erro(422, "midia_invalida", "Arquivo de mídia não encontrado. Envie-o primeiro em POST /midias.")
    m = snap.to_dict()
    if m["tipo"] != tipo:
        raise erro(422, "midia_tipo_errado", f"O arquivo informado não é do tipo '{tipo}'.")
    return m


@router.post("/categorias/{cid}/botoes", status_code=201)
def criar_botao(cid: str, dados: BotaoIn, u=Depends(usuario_atual), db=Depends(get_db)):
    ref, cat = _carregar(db, u["uid"], cid)
    botoes = cat.get("botoes", [])
    if len(botoes) >= settings.max_botoes_por_categoria:
        raise erro(409, "limite_botoes", f"Cada categoria comporta no máximo {settings.max_botoes_por_categoria} botões.")
    img, aud = _midia(db, u["uid"], dados.imagem_id, "imagem"), _midia(db, u["uid"], dados.audio_id, "audio")
    botao = {"id": uuid.uuid4().hex[:12], "rotulo": dados.rotulo, "significado": dados.significado or dados.rotulo,
             "imagem_id": dados.imagem_id, "imagem": img["nome_original"] if img else None,
             "audio_id": dados.audio_id, "audio": aud["nome_original"] if aud else None, "ordem": len(botoes)}
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
    campos = dados.model_dump(exclude_unset=True)
    if "rotulo" in campos:
        if not campos["rotulo"] or not campos["rotulo"].strip():
            raise erro(422, "validacao", "O rótulo não pode ser vazio.")
        b["rotulo"] = " ".join(campos["rotulo"].split())
    if "significado" in campos:
        b["significado"] = campos["significado"]
    for chave, tipo, nome in (("imagem_id", "imagem", "imagem"), ("audio_id", "audio", "audio")):
        if chave in campos:
            m = _midia(db, u["uid"], campos[chave], tipo)
            b[chave], b[nome] = campos[chave], (m["nome_original"] if m else None)
    ref.update({"botoes": botoes})
    bump_dispositivos(db, u["uid"])
    return b


@router.delete("/categorias/{cid}/botoes/{bid}", status_code=204)
def excluir_botao(cid: str, bid: str, u=Depends(usuario_atual), db=Depends(get_db)):
    ref, cat = _carregar(db, u["uid"], cid)
    restantes = [b for b in cat.get("botoes", []) if b["id"] != bid]
    if len(restantes) == len(cat.get("botoes", [])):
        raise erro(404, "nao_encontrado", "Botão não encontrado.")
    removido = next(b for b in cat["botoes"] if b["id"] == bid)
    ref.update({"botoes": restantes})
    liberar_midias(db, u["uid"], {m for m in (removido.get("imagem_id"), removido.get("audio_id")) if m})
    bump_dispositivos(db, u["uid"])


def _ordem_valida(atuais: list[str], novos: list[str], nome: str):
    if sorted(atuais) != sorted(novos):
        raise erro(422, "ordem_invalida", f"A lista deve conter exatamente todos os {nome}, sem repetir.")


@router.put("/categorias/ordem", summary="Reordena as categorias (envie todos os ids na nova ordem)")
def ordenar_categorias(dados: OrdemIn, u=Depends(usuario_atual), db=Depends(get_db)):
    cats = _todas(db, u["uid"])
    _ordem_valida([c["id"] for c in cats], dados.ids, "categorias")
    for pos, cid in enumerate(dados.ids):
        _col(db, u["uid"]).document(cid).update({"ordem": pos})
    bump_dispositivos(db, u["uid"])
    return _todas(db, u["uid"])


@router.put("/categorias/{cid}/botoes/ordem", summary="Reordena os botões de uma categoria")
def ordenar_botoes(cid: str, dados: OrdemIn, u=Depends(usuario_atual), db=Depends(get_db)):
    ref, cat = _carregar(db, u["uid"], cid)
    botoes = cat.get("botoes", [])
    _ordem_valida([b["id"] for b in botoes], dados.ids, "botões")
    por_id = {b["id"]: b for b in botoes}
    novos = [{**por_id[i], "ordem": pos} for pos, i in enumerate(dados.ids)]
    ref.update({"botoes": novos})
    bump_dispositivos(db, u["uid"])
    return novos
