"""Envio de e-mail por SMTP.

- Sem SMTP_HOST: modo desenvolvimento. NENHUM e-mail é enviado; o conteúdo vai para o log e para `outbox` (testes).
- Com SMTP_HOST: STARTTLS (porta 587) ou SSL (porta 465), SEMPRE verificando o certificado do servidor.
- `enviar_email` devolve True/False, para quem chama poder avisar o usuário quando o envio falha.
"""
import logging
import smtplib
import socket
import ssl
from email.message import EmailMessage
from email.utils import formataddr, parseaddr

from .config import settings

log = logging.getLogger("uvicorn.error")
outbox: list[dict] = []


def remetente() -> str:
    """SMTP_FROM, ou o próprio SMTP_USER (o Gmail rejeita/reescreve remetentes diferentes da conta)."""
    return settings.smtp_from or settings.smtp_user or "nao-responder@casa.local"


def smtp_configurado() -> bool:
    return bool(settings.smtp_host)


def _mascarar(email: str) -> str:
    nome, _, dominio = email.partition("@")
    return f"{nome[:1]}***@{dominio}" if dominio else "***"


def _abrir_conexao():
    contexto = ssl.create_default_context()  # verifica certificado e nome do servidor (o padrão do starttls() NÃO verifica)
    if settings.smtp_ssl or settings.smtp_port == 465:
        s = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=settings.smtp_timeout, context=contexto)
    else:
        s = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=settings.smtp_timeout)
        s.ehlo()
        if settings.smtp_tls:
            s.starttls(context=contexto)
            s.ehlo()
    try:
        if settings.smtp_user:
            s.login(settings.smtp_user, settings.smtp_password)
    except Exception:
        s.close()
        raise
    return s


def explicar_erro(e: Exception) -> str:
    """Traduz o erro técnico para uma ação concreta."""
    if isinstance(e, smtplib.SMTPAuthenticationError):
        return ("usuário ou senha recusados pelo servidor. No Gmail é preciso ativar a verificação em 2 etapas "
                "e usar uma 'Senha de app' (não a senha normal da conta).")
    if isinstance(e, ssl.SSLCertVerificationError):
        return "o certificado do servidor SMTP não é confiável (ou o nome do servidor não confere com SMTP_HOST)."
    if isinstance(e, (socket.timeout, TimeoutError)):
        return "tempo esgotado ao falar com o servidor SMTP (porta bloqueada por firewall/antivírus, ou host errado)."
    if isinstance(e, (ConnectionRefusedError, socket.gaierror)):
        return "não foi possível conectar ao servidor SMTP: confira SMTP_HOST e SMTP_PORT (587 com STARTTLS ou 465 com SSL)."
    if isinstance(e, smtplib.SMTPNotSupportedError):
        return "o servidor não oferece o recurso pedido (tente SMTP_PORT=465 com SMTP_SSL=true, ou SMTP_TLS=false em servidor local)."
    if isinstance(e, smtplib.SMTPSenderRefused):
        return "o servidor recusou o remetente: SMTP_FROM deve ser o mesmo e-mail de SMTP_USER."
    if isinstance(e, smtplib.SMTPRecipientsRefused):
        return "o servidor recusou o destinatário."
    return f"{type(e).__name__}: {e}"


def verificar_smtp() -> tuple[bool, str]:
    """Conecta e autentica, sem enviar nada. Usado por `python -m app.testar_smtp`."""
    if not smtp_configurado():
        return False, "SMTP_HOST está vazio: modo desenvolvimento (nenhum e-mail é enviado; o código aparece no terminal)."
    try:
        with _abrir_conexao() as s:
            s.noop()
        return True, f"conexão e autenticação OK em {settings.smtp_host}:{settings.smtp_port}."
    except Exception as e:
        return False, explicar_erro(e)


def enviar_email(para: str, assunto: str, corpo: str) -> bool:
    if not smtp_configurado():
        outbox.append({"para": para, "assunto": assunto, "corpo": corpo})
        del outbox[:-50]
        log.warning("[E-MAIL DE DESENVOLVIMENTO — SMTP não configurado, nada foi enviado] para=%s\n%s", para, corpo)
        return True
    msg = EmailMessage()
    nome, endereco = parseaddr(remetente())
    msg["From"] = formataddr((nome or "C.A.S.A.", endereco))
    msg["To"], msg["Subject"] = para, assunto
    msg.set_content(corpo)
    try:
        with _abrir_conexao() as s:
            s.send_message(msg)
        log.info("E-mail enviado para %s", _mascarar(para))
        return True
    except Exception as e:
        log.error("Falha ao enviar e-mail para %s: %s", _mascarar(para), explicar_erro(e))
        return False


def corpo_codigo(nome: str, codigo: str, validade_min: int) -> str:
    return (f"Olá, {nome}!\n\nUse o código abaixo para confirmar seu e-mail e concluir o cadastro no C.A.S.A.\n\n"
            f"Seu código: {codigo}\n\nEle expira em {validade_min} minutos. "
            "Se você não solicitou este cadastro, ignore esta mensagem.\n\n— Equipe C.A.S.A.")
