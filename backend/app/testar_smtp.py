"""Diagnóstico do SMTP.   Uso (dentro de backend/, com o venv ativo):

    python -m app.testar_smtp                    # só confere conexão e login
    python -m app.testar_smtp voce@gmail.com     # confere e envia um e-mail de teste
"""
import sys

from . import emailer
from .config import settings


def main(argv: list[str]) -> int:
    print("=== Configuração lida do .env ===")
    print(f"SMTP_HOST     : {settings.smtp_host or '(vazio)'}")
    print(f"SMTP_PORT     : {settings.smtp_port}  ({'SSL direto' if settings.smtp_ssl or settings.smtp_port == 465 else 'STARTTLS' if settings.smtp_tls else 'sem criptografia'})")
    print(f"SMTP_USER     : {emailer._mascarar(settings.smtp_user) if settings.smtp_user else '(vazio)'}")
    print(f"SMTP_PASSWORD : {'definida (' + str(len(settings.smtp_password)) + ' caracteres)' if settings.smtp_password else '(vazia)'}")
    print(f"Remetente     : {emailer.remetente()}")
    ok, msg = emailer.verificar_smtp()
    print(("\n[OK] " if ok else "\n[FALHOU] ") + msg)
    if ok and argv:
        enviado = emailer.enviar_email(argv[0], "C.A.S.A. — teste de e-mail", "Se você recebeu esta mensagem, o SMTP do C.A.S.A. está funcionando.")
        print(f"[{'OK' if enviado else 'FALHOU'}] envio de teste para {emailer._mascarar(argv[0])}" + ("" if enviado else " (veja o motivo acima, nos logs)"))
        return 0 if enviado else 1
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
