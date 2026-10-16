"""Perfil do responsável. Cadastro/login/recuperação de senha são feitos NO FRONTEND pelo Firebase Auth."""
from fastapi import APIRouter, Depends

from ..deps import get_auth, get_db, usuario_atual
from ..schemas import PerfilIn
from ..util import agora_iso

router = APIRouter(prefix="/me", tags=["Perfil"])

PADRAO = {"notificacoes_ativas": True, "modo_escuro": False, "tamanho_fonte": 10}


@router.get("", summary="Retorna o perfil; cria o documento no 1º acesso (use logo após o login)")
def meu_perfil(u: dict = Depends(usuario_atual), db=Depends(get_db)):
    ref = db.collection("usuarios").document(u["uid"])
    snap = ref.get()
    if not snap.exists:
        ref.set({"nome": u.get("nome") or (u["email"] or "").split("@")[0], "email": u["email"], "criado_em": agora_iso(), **PADRAO})
        snap = ref.get()
    return {"uid": u["uid"], **snap.to_dict()}


@router.patch("", summary="Atualiza nome e preferências (notificações, modo escuro, fonte 8–20)")
def atualizar(dados: PerfilIn, u: dict = Depends(usuario_atual), db=Depends(get_db)):
    ref = db.collection("usuarios").document(u["uid"])
    campos = dados.model_dump(exclude_none=True)
    if campos:
        ref.set(campos, merge=True)
    return {"uid": u["uid"], **ref.get().to_dict()}


@router.get("/exportar", summary="LGPD: exporta todos os meus dados")
def exportar(u: dict = Depends(usuario_atual), db=Depends(get_db)):
    from ..util import filtro
    raiz = db.collection("usuarios").document(u["uid"])
    snap = raiz.get()
    return {
        "perfil": snap.to_dict() if snap.exists else {},
        "categorias": [{"id": s.id, **s.to_dict()} for s in raiz.collection("categorias").stream()],
        "acionamentos": [s.to_dict() for s in raiz.collection("acionamentos").stream()],
        "notificacoes": [s.to_dict() for s in raiz.collection("notificacoes").stream()],
        "dispositivos": [{k: v for k, v in d.to_dict().items() if k != "token_hash"}
                         for d in db.collection("dispositivos").where(filter=filtro("owner_uid", u["uid"])).stream()],
    }


@router.delete("", status_code=204, summary="Exclui a conta e TODOS os dados (LGPD)")
def excluir(u: dict = Depends(usuario_atual), db=Depends(get_db), fb=Depends(get_auth)):
    uid = u["uid"]
    from ..util import filtro
    for d in db.collection("dispositivos").where(filter=filtro("owner_uid", uid)).stream():
        d.reference.delete()
    from .. import storage
    for m in db.collection("usuarios").document(uid).collection("midias").stream():
        storage.remover(m.to_dict()["arquivo"])
    db.recursive_delete(db.collection("usuarios").document(uid))  # categorias, histórico etc.
    fb.delete_user(uid)
