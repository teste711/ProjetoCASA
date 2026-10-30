"""Testes do SMTP contra um servidor SMTP DE VERDADE (aiosmtpd, em 127.0.0.1), não contra mocks.

Cobrem: entrega e formato da mensagem, STARTTLS e SSL direto COM verificação de certificado, login certo e errado,
mensagens de diagnóstico e que a senha nunca vaza (nem no log, nem no diagnóstico)."""
import datetime
import email
import ipaddress
import logging
import socket
import ssl
from email import policy

import pytest

pytest.importorskip("aiosmtpd")
from aiosmtpd.controller import Controller  # noqa: E402
from aiosmtpd.smtp import AuthResult, LoginPassword  # noqa: E402
from cryptography import x509  # noqa: E402
from cryptography.hazmat.primitives import hashes, serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric import rsa  # noqa: E402
from cryptography.x509.oid import NameOID  # noqa: E402

from app import emailer, testar_smtp  # noqa: E402

USUARIO, SENHA = "casa@exemplo.com", "senha-de-app-1234"
real_create_default_context = ssl.create_default_context


def _porta_livre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def certificado(tmp_path_factory):
    """Certificado autoassinado para 127.0.0.1 (NÃO é confiável pelo sistema: serve para provar a verificação)."""
    d = tmp_path_factory.mktemp("cert")
    chave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nome = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "127.0.0.1")])
    agora = datetime.datetime.now(datetime.timezone.utc)
    cert = (x509.CertificateBuilder().subject_name(nome).issuer_name(nome).public_key(chave.public_key())
            .serial_number(x509.random_serial_number()).not_valid_before(agora - datetime.timedelta(minutes=5))
            .not_valid_after(agora + datetime.timedelta(days=1))
            .add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]), critical=False)
            .sign(chave, hashes.SHA256()))
    crt, key = d / "cert.pem", d / "key.pem"
    crt.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key.write_bytes(chave.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL,
                                        serialization.NoEncryption()))
    return crt, key


class Caixa:
    def __init__(self):
        self.recebidas = []

    async def handle_DATA(self, server, session, envelope):
        self.recebidas.append(envelope)
        return "250 Mensagem aceita"


def _autenticador(server, session, envelope, mechanism, auth_data):
    ok = isinstance(auth_data, LoginPassword) and auth_data.login == USUARIO.encode() and auth_data.password == SENHA.encode()
    return AuthResult(success=ok, handled=ok)


def _servidor(**kw):
    caixa = Caixa()
    porta = _porta_livre()
    ctl = Controller(caixa, hostname="127.0.0.1", port=porta, **kw)
    ctl.start()
    return ctl, caixa, porta


def _configurar(monkeypatch, porta, *, tls=False, ssl_direto=False, usuario="", senha="", confiar=None):
    for k, v in dict(smtp_host="127.0.0.1", smtp_port=porta, smtp_tls=tls, smtp_ssl=ssl_direto, smtp_user=usuario,
                     smtp_password=senha, smtp_from="C.A.S.A. <casa@exemplo.com>", smtp_timeout=5).items():
        monkeypatch.setattr(emailer.settings, k, v)
    if confiar:  # faz o cliente confiar no certificado de teste (a verificação continua LIGADA)
        monkeypatch.setattr(emailer.ssl, "create_default_context", lambda *a, **k: real_create_default_context(cafile=str(confiar)))


def _ctx_servidor(certificado):
    c = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    c.load_cert_chain(*map(str, certificado))
    return c


def test_modo_desenvolvimento_nao_envia_e_avisa(monkeypatch, caplog):
    monkeypatch.setattr(emailer.settings, "smtp_host", "")
    emailer.outbox.clear()
    with caplog.at_level(logging.WARNING, logger="uvicorn.error"):
        assert emailer.enviar_email("a@b.com", "assunto", "corpo") is True
    assert emailer.outbox[-1]["para"] == "a@b.com"
    assert "nada foi enviado" in caplog.text
    ok, msg = emailer.verificar_smtp()
    assert ok is False and "SMTP_HOST está vazio" in msg


def test_entrega_a_mensagem_com_cabecalhos_e_acentos(monkeypatch):
    ctl, caixa, porta = _servidor()
    try:
        _configurar(monkeypatch, porta)
        corpo = emailer.corpo_codigo("José Ávila", "123456", 15)
        assert emailer.enviar_email("pai@exemplo.com", "C.A.S.A. — seu código de confirmação", corpo) is True
    finally:
        ctl.stop()
    env = caixa.recebidas[0]
    msg = email.message_from_bytes(env.content, policy=policy.default)
    assert env.rcpt_tos == ["pai@exemplo.com"] and env.mail_from == "casa@exemplo.com"
    assert msg["Subject"] == "C.A.S.A. — seu código de confirmação" and "casa@exemplo.com" in msg["From"]
    assert "José Ávila" in msg.get_content() and "Seu código: 123456" in msg.get_content()


def test_starttls_recusa_certificado_nao_confiavel(monkeypatch, certificado, caplog):
    """Prova a correção: antes o starttls() aceitava QUALQUER certificado (verify_mode=0), permitindo interceptação."""
    ctl, caixa, porta = _servidor(tls_context=_ctx_servidor(certificado), require_starttls=True)
    try:
        _configurar(monkeypatch, porta, tls=True)               # NÃO confia no certificado autoassinado
        with caplog.at_level(logging.ERROR, logger="uvicorn.error"):
            assert emailer.enviar_email("pai@exemplo.com", "x", "corpo") is False
        ok, msg = emailer.verificar_smtp()
    finally:
        ctl.stop()
    assert caixa.recebidas == []                                # nada foi entregue
    assert ok is False and "certificado" in msg and "confiável" in msg
    assert "certificado" in caplog.text


def test_starttls_com_certificado_confiavel_e_login(monkeypatch, certificado):
    ctl, caixa, porta = _servidor(tls_context=_ctx_servidor(certificado), require_starttls=True,
                                  authenticator=_autenticador, auth_required=True)
    try:
        _configurar(monkeypatch, porta, tls=True, usuario=USUARIO, senha=SENHA, confiar=certificado[0])
        assert emailer.verificar_smtp()[0] is True
        assert emailer.enviar_email("pai@exemplo.com", "assunto", "corpo") is True
    finally:
        ctl.stop()
    assert len(caixa.recebidas) == 1


def test_ssl_direto_porta_465_estilo(monkeypatch, certificado):
    # a conexão já nasce criptografada; o aiosmtpd só não a reconhece como TLS ao anunciar o AUTH, então
    # desligamos essa exigência NO SERVIDOR DE TESTE (o cliente continua verificando o certificado)
    ctl, caixa, porta = _servidor(ssl_context=_ctx_servidor(certificado), authenticator=_autenticador,
                                  auth_required=True, auth_require_tls=False)
    try:
        _configurar(monkeypatch, porta, ssl_direto=True, usuario=USUARIO, senha=SENHA, confiar=certificado[0])
        assert emailer.enviar_email("pai@exemplo.com", "assunto ssl", "corpo") is True
    finally:
        ctl.stop()
    assert len(caixa.recebidas) == 1


def test_senha_errada_da_diagnostico_util_e_nao_vaza_a_senha(monkeypatch, certificado, caplog, capsys):
    ctl, caixa, porta = _servidor(tls_context=_ctx_servidor(certificado), require_starttls=True,
                                  authenticator=_autenticador, auth_required=True)
    try:
        _configurar(monkeypatch, porta, tls=True, usuario=USUARIO, senha="SENHA-ERRADA-999", confiar=certificado[0])
        with caplog.at_level(logging.DEBUG, logger="uvicorn.error"):
            assert emailer.enviar_email("pai@exemplo.com", "x", "corpo") is False
        ok, msg = emailer.verificar_smtp()
        codigo = testar_smtp.main([])
    finally:
        ctl.stop()
    saida = capsys.readouterr().out
    assert ok is False and "Senha de app" in msg and caixa.recebidas == []
    assert codigo == 1 and "[FALHOU]" in saida
    for texto in (caplog.text, msg, saida):                    # a senha NUNCA aparece
        assert "SENHA-ERRADA-999" not in texto
    assert "(" in saida and "caracteres)" in saida              # só informa que existe e o tamanho


def test_servidor_inexistente_e_porta_fechada(monkeypatch):
    _configurar(monkeypatch, _porta_livre())                    # ninguém escutando
    assert emailer.enviar_email("a@b.com", "x", "y") is False
    ok, msg = emailer.verificar_smtp()
    assert ok is False and "SMTP_HOST" in msg


def test_cli_envia_e_mascara_o_destinatario(monkeypatch, capsys):
    ctl, caixa, porta = _servidor()
    try:
        _configurar(monkeypatch, porta)
        assert testar_smtp.main(["pessoa@exemplo.com"]) == 0
    finally:
        ctl.stop()
    saida = capsys.readouterr().out
    assert "[OK]" in saida and "p***@exemplo.com" in saida and "pessoa@exemplo.com" not in saida
    assert len(caixa.recebidas) == 1


def test_remetente_usa_smtp_user_quando_smtp_from_vazio(monkeypatch):
    monkeypatch.setattr(emailer.settings, "smtp_from", "")
    monkeypatch.setattr(emailer.settings, "smtp_user", "conta@gmail.com")
    assert emailer.remetente() == "conta@gmail.com"


def test_cadastro_devolve_503_e_nao_deixa_pendente_quando_o_smtp_falha(monkeypatch):
    from fastapi.testclient import TestClient
    from app.deps import Limitador, get_auth, get_db
    from app.main import app
    from tests.fakes import FakeAuth, FakeFirestore
    db, fb = FakeFirestore(), FakeAuth()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_auth] = lambda: fb
    Limitador._hits.clear()
    try:
        _configurar(monkeypatch, _porta_livre())                # SMTP configurado, mas fora do ar
        r = TestClient(app).post("/auth/cadastro", json={"nome": "Ana", "email": "ana@x.com", "senha": "Senha@123"})
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 503 and r.json()["codigo"] == "email_indisponivel"
    assert db.data == {} and fb.usuarios == {}                  # nada pendente, nenhuma conta
