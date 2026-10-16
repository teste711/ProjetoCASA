"""Envio de e-mail (SMTP). Sem SMTP_HOST, o conteúdo vai só para o log (e para `outbox`, usado nos testes)."""
import logging
import smtplib
from email.message import EmailMessage

from .config import settings

log = logging.getLogger("uvicorn.error")
outbox: list[dict] = []


def enviar_email(para: str, assunto: str, corpo: str) -> None:
    if not settings.smtp_host:
        outbox.append({"para": para, "assunto": assunto, "corpo": corpo})
        del outbox[:-50]
        log.warning("[E-MAIL DE DESENVOLVIMENTO — SMTP não configurado] para=%s\n%s", para, corpo)
        return
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = settings.smtp_from, para, assunto
    msg.set_content(corpo)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as s:
            if settings.smtp_tls:
                s.starttls()
            if settings.smtp_user:
                s.login(settings.smtp_user, settings.smtp_password)
            s.send_message(msg)
    except Exception:  # roda em segundo plano: não derruba a requisição
        log.exception("Falha ao enviar e-mail para %s", para)


def corpo_codigo(nome: str, codigo: str, validade_min: int) -> str:
    return (f"Olá, {nome}!\n\nUse o código abaixo para confirmar seu e-mail e concluir o cadastro no C.A.S.A.\n\n"
            f"Seu código: {codigo}\n\nEle expira em {validade_min} minutos. "
            "Se você não solicitou este cadastro, ignore esta mensagem.\n\n— Equipe C.A.S.A.")
