import re
from pydantic import BaseModel, EmailStr, Field, field_validator

from .config import settings


_MAC = re.compile(r"^([0-9A-Fa-f]{2}[:\-]?){5}[0-9A-Fa-f]{2}$")


class PerfilIn(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=120)
    notificacoes_ativas: bool | None = None
    modo_escuro: bool | None = None
    tamanho_fonte: int | None = Field(default=None, ge=8, le=20)


class BotaoIn(BaseModel):
    rotulo: str = Field(min_length=1, max_length=60)
    significado: str | None = Field(default=None, max_length=200)
    imagem_id: str | None = None   # id retornado por POST /midias
    audio_id: str | None = None


class BotaoUpdate(BaseModel):
    rotulo: str | None = Field(default=None, min_length=1, max_length=60)
    significado: str | None = None
    imagem_id: str | None = None   # envie null para remover
    audio_id: str | None = None


class CategoriaIn(BaseModel):
    nome: str = Field(min_length=1, max_length=60)
    cor: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")


def normalizar_mac(v: str) -> str:
    if not _MAC.match(v.strip()):
        raise ValueError("Endereço MAC inválido. Use AA:BB:CC:DD:EE:FF.")
    h = re.sub(r"[^0-9A-Fa-f]", "", v).upper()
    return ":".join(h[i:i + 2] for i in range(0, 12, 2))


class DispositivoIn(BaseModel):
    mac: str
    nome: str | None = Field(default=None, max_length=80)
    nome_paciente: str | None = Field(default=None, max_length=120)

    _mac_ok = field_validator("mac")(lambda cls, v: normalizar_mac(v))


class DispositivoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=80)
    nome_paciente: str | None = Field(default=None, max_length=120)
    modo: str | None = Field(default=None, max_length=20)
    volume: int | None = Field(default=None, ge=0, le=100)
    brilho_leds: int | None = Field(default=None, ge=0, le=100)
    brilho_telas: int | None = Field(default=None, ge=0, le=100)
    tempo_inatividade_s: int | None = Field(default=None, ge=10, le=3600)


class AcionamentoDispositivo(BaseModel):
    botao_id: str
    uid_local: str = Field(pattern=r"^[A-Za-z0-9_-]{1,64}$")  # id gerado no ESP32 (evita duplicar no reenvio)
    ha_segundos: int = Field(default=0, ge=0, le=60 * 60 * 24 * 30)


class Telemetria(BaseModel):
    bateria_pct: int | None = Field(default=None, ge=0, le=100)
    carregando: bool | None = None
    ip: str | None = Field(default=None, max_length=45)
    firmware: str | None = Field(default=None, max_length=30)
    ssid: str | None = Field(default=None, max_length=32)       # rede Wi-Fi atual
    sinal_wifi: int | None = Field(default=None, ge=0, le=100)  # intensidade em %
    acionamentos: list[AcionamentoDispositivo] = Field(default_factory=list, max_length=500)


class OrdemIn(BaseModel):
    ids: list[str] = Field(min_length=1)


class AcionamentoApp(BaseModel):
    botao_id: str


_REGRA_SENHA = "A senha deve ter no mínimo 8 caracteres, uma letra maiúscula e um número ou caractere especial."


def validar_senha(v: str) -> str:
    """Mesma regra do formulário de cadastro."""
    if len(v) < 8 or not re.search(r"[A-Z]", v) or not re.search(r'[0-9!@#$%^&*(),.?":{}|<>]', v):
        raise ValueError(_REGRA_SENHA)
    if len(v) > 128:
        raise ValueError("A senha deve ter no máximo 128 caracteres.")
    return v


class CadastroIn(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    senha: str

    @field_validator("nome")
    @classmethod
    def _nome(cls, v: str) -> str:
        v = " ".join(v.split())
        if len(v) < 2:
            raise ValueError("Informe um nome válido.")
        return v

    _senha = field_validator("senha")(validar_senha)


class ConfirmarIn(BaseModel):
    email: EmailStr
    codigo: str = Field(pattern=r"^\d{6}$")
    senha: str   # reenviada aqui: o servidor NÃO guarda a senha entre as duas etapas

    _senha = field_validator("senha")(validar_senha)


class ReenviarIn(BaseModel):
    email: EmailStr


class ConclusaoIn(BaseModel):
    sha256: str | None = Field(default=None, pattern=r"^[0-9a-fA-F]{64}$")  # hash dos bytes que o aparelho decodificou


class ErroIn(BaseModel):
    mensagem: str = Field(min_length=1, max_length=200)
