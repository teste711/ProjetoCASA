"""Imagens (pictogramas) e áudios dos botões. Arquivos em disco; metadados em usuarios/{uid}/midias."""
import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse

from .. import storage
from ..config import settings
from ..deps import Limitador, erro, get_db, usuario_atual
from ..util import agora_iso, bump_dispositivos

router = APIRouter(prefix="/midias", tags=["Mídias (imagens e áudios)"])


def _col(db, uid):
    return db.collection("usuarios").document(uid).collection("midias")


@router.post("", status_code=201, dependencies=[Depends(Limitador(30, 60))],
             summary="Envia imagem (PNG/JPEG/WEBP) ou áudio (MP3/WAV). O tipo é detectado pelo CONTEÚDO")
def enviar(arquivo: UploadFile = File(...), tipo: str | None = Form(default=None),
           u=Depends(usuario_atual), db=Depends(get_db)):
    if tipo not in (None, "imagem", "audio"):
        raise erro(422, "validacao", "O tipo deve ser 'imagem' ou 'audio'.")
    if len(list(_col(db, u["uid"]).stream())) >= settings.max_midias_por_usuario:
        raise erro(409, "limite_midias", f"Limite de {settings.max_midias_por_usuario} arquivos atingido.")
    limite = max(settings.max_imagem_mb, settings.max_audio_mb) * 1024 * 1024
    dados = arquivo.file.read(limite + 1)
    if not dados:
        raise erro(422, "arquivo_vazio", "O arquivo enviado está vazio.")
    if len(dados) > limite:
        raise erro(413, "arquivo_grande", "Arquivo muito grande.")

    audio = storage.detectar_audio(dados)
    if audio and tipo != "imagem":
        if len(dados) > settings.max_audio_mb * 1024 * 1024:
            raise erro(413, "arquivo_grande", f"O áudio excede {settings.max_audio_mb} MB.")
        mime, ext, tipo_final = audio[0], audio[1], "audio"
    else:
        if tipo == "audio":
            raise erro(415, "audio_invalido", "Envie um áudio MP3 ou WAV válido.")
        if len(dados) > settings.max_imagem_mb * 1024 * 1024:
            raise erro(413, "arquivo_grande", f"A imagem excede {settings.max_imagem_mb} MB.")
        dados, mime, ext, tipo_final = storage.processar_imagem(dados), "image/jpeg", ".jpg", "imagem"

    nome_disco, sha = storage.salvar(dados, ext)
    nome = (arquivo.filename or f"arquivo{ext}").replace("\\", "/").split("/")[-1][:255]
    mid = uuid.uuid4().hex[:16]
    meta = {"tipo": tipo_final, "nome_original": nome, "arquivo": nome_disco, "mime": mime,
            "tamanho": len(dados), "sha256": sha, "criado_em": agora_iso()}
    _col(db, u["uid"]).document(mid).set(meta)
    return {"id": mid, **{k: v for k, v in meta.items() if k != "arquivo"}}


@router.get("")
def listar(tipo: str | None = None, u=Depends(usuario_atual), db=Depends(get_db)):
    itens = [{"id": s.id, **{k: v for k, v in s.to_dict().items() if k != "arquivo"}} for s in _col(db, u["uid"]).stream()]
    return [i for i in itens if tipo not in ("imagem", "audio") or i["tipo"] == tipo]


@router.get("/{mid}/arquivo", summary="Baixa o arquivo (exige o token; no frontend use responseType blob)")
def baixar(mid: str, u=Depends(usuario_atual), db=Depends(get_db)):
    snap = _col(db, u["uid"]).document(mid).get()
    if not snap.exists:
        raise erro(404, "nao_encontrado", "Arquivo não encontrado.")
    m = snap.to_dict()
    return FileResponse(storage.caminho(m["arquivo"]), media_type=m["mime"], filename=m["nome_original"],
                        content_disposition_type="inline", headers={"X-Content-Type-Options": "nosniff"})


@router.delete("/{mid}", status_code=204, summary="Exclui o arquivo e o remove dos botões que o usavam")
def excluir(mid: str, u=Depends(usuario_atual), db=Depends(get_db)):
    ref = _col(db, u["uid"]).document(mid)
    snap = ref.get()
    if not snap.exists:
        raise erro(404, "nao_encontrado", "Arquivo não encontrado.")
    for s in db.collection("usuarios").document(u["uid"]).collection("categorias").stream():
        botoes, mudou = s.to_dict().get("botoes", []), False
        for b in botoes:
            if b.get("imagem_id") == mid:
                b["imagem_id"], b["imagem"], mudou = None, None, True
            if b.get("audio_id") == mid:
                b["audio_id"], b["audio"], mudou = None, None, True
        if mudou:
            s.reference.update({"botoes": botoes})
    storage.remover(snap.to_dict()["arquivo"])
    ref.delete()
    bump_dispositivos(db, u["uid"])
