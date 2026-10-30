"""Cadastro que SÓ cria a conta no Firebase depois de confirmar o e-mail com um código.

Etapa 1  POST /auth/cadastro   → valida, grava um cadastro PENDENTE e envia o código por e-mail.
Etapa 2  POST /auth/confirmar  → confere o código e então cria o usuário no Firebase Auth (e-mail verificado).
Depois o frontend faz o login normal com signInWithEmailAndPassword.
Login e "esqueci a senha" continuam sendo do Firebase (frontend)."""
import hashlib
import threading
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends

from ..config import settings
from ..deps import Limitador, erro, get_auth, get_db
from ..emailer import corpo_codigo, enviar_email
from ..firebase import EmailJaExiste
from ..schemas import CadastroIn, ConfirmarIn, ReenviarIn
from ..security import codigo_confere, gerar_codigo, hash_codigo

router = APIRouter(prefix="/auth", tags=["Cadastro com e-mail confirmado"])
_limite = Depends(Limitador(10, 60))
# Serializa "ler → contar tentativa → comparar": sem isso, requisições paralelas leriam o mesmo
# contador e testariam centenas de códigos de uma vez. (Com VÁRIOS servidores, troque por transação do Firestore.)
_trava = threading.Lock()


def _pendente(db, email: str):
    return db.collection("cadastros_pendentes").document(hashlib.sha256(email.encode()).hexdigest()[:32])


def _agora() -> datetime:
    return datetime.now(timezone.utc)


def _emitir(db, email: str, nome: str) -> None:
    """Grava o cadastro pendente e ENVIA o e-mail na hora. Se o e-mail não sair, o pendente é descartado e o
    usuário recebe um erro claro (antes, a falha só aparecia no terminal e a tela dizia "código enviado")."""
    ref = _pendente(db, email)
    atual = ref.get()
    if atual.exists:
        ultimo = datetime.fromisoformat(atual.to_dict()["enviado_em"])
        if (_agora() - ultimo).total_seconds() < settings.codigo_reenvio_segundos:
            raise erro(429, "aguarde_reenvio", "Aguarde alguns segundos antes de pedir um novo código.")
    codigo = gerar_codigo()
    ref.set({"nome": nome, "email": email, "codigo_hash": hash_codigo(email, codigo), "tentativas": 0,
             "enviado_em": _agora().isoformat(),
             "expira_em": (_agora() + timedelta(minutes=settings.codigo_validade_minutos)).isoformat()})
    if not enviar_email(email, "C.A.S.A. — seu código de confirmação", corpo_codigo(nome, codigo, settings.codigo_validade_minutos)):
        ref.delete()
        raise erro(503, "email_indisponivel", "Não foi possível enviar o e-mail agora. Tente novamente em instantes.")


@router.post("/cadastro", status_code=202, dependencies=[_limite],
             summary="Etapa 1: envia o código de confirmação (ainda NÃO cria a conta)")
def cadastro(dados: CadastroIn, db=Depends(get_db), fb=Depends(get_auth)):
    email = dados.email.lower()
    if fb.email_existe(email):
        raise erro(409, "email_em_uso", "Este e-mail já está cadastrado.")
    _emitir(db, email, dados.nome)
    return {"mensagem": "Enviamos um código de confirmação para o seu e-mail.", "email": email,
            "expira_em_minutos": settings.codigo_validade_minutos}


@router.post("/reenviar-codigo", status_code=202, dependencies=[_limite], summary="Reenvia o código (cooldown de 60 s)")
def reenviar(dados: ReenviarIn, db=Depends(get_db)):
    email = dados.email.lower()
    atual = _pendente(db, email).get()
    if atual.exists:  # resposta idêntica exista pendência ou não (não revela nada)
        _emitir(db, email, atual.to_dict()["nome"])
    return {"mensagem": "Se houver um cadastro pendente para este e-mail, enviamos um novo código."}


@router.post("/confirmar", status_code=201, dependencies=[_limite],
             summary="Etapa 2: confere o código e cria a conta no Firebase")
def confirmar(dados: ConfirmarIn, db=Depends(get_db), fb=Depends(get_auth)):
    email = dados.email.lower()
    ref = _pendente(db, email)
    invalido = erro(400, "codigo_invalido", "Código inválido. Verifique e tente novamente.")
    with _trava:
        snap = ref.get()
        if not snap.exists:
            raise invalido
        p = snap.to_dict()
        if datetime.fromisoformat(p["expira_em"]) < _agora():
            ref.delete()
            raise erro(400, "codigo_expirado", "O código expirou. Volte e peça um novo.")
        if p["tentativas"] >= settings.codigo_max_tentativas:
            ref.delete()
            raise erro(429, "codigo_bloqueado", "Tentativas excedidas. Volte e peça um novo código.")
        ref.update({"tentativas": p["tentativas"] + 1})  # conta ANTES de comparar
        confere = codigo_confere(email, dados.codigo, p["codigo_hash"])
    if not confere:
        raise invalido
    try:
        fb.create_user(email, dados.senha, p["nome"])
    except EmailJaExiste:
        ref.delete()
        raise erro(409, "email_em_uso", "Este e-mail já está cadastrado.")
    ref.delete()
    return {"mensagem": "Conta criada com sucesso! Faça login para continuar."}
