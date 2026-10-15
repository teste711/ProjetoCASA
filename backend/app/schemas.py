import re
from pydantic import BaseModel, Field, field_validator

_MAC = re.compile(r"^([0-9A-Fa-f]{2}[:\-]?){5}[0-9A-Fa-f]{2}$")


class PerfilIn(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=120)
    notificacoes_ativas: bool | None = None
    modo_escuro: bool | None = None
    tamanho_fonte: int | None = Field(default=None, ge=8, le=20)


class BotaoIn(BaseModel):
    rotulo: str = Field(min_length=1, max_length=60)
    significado: str | None = Field(default=None, max_length=200)
    imagem_url: str | None = Field(default=None, max_length=1000)  # URL do Firebase Storage
    audio_url: str | None = Field(default=None, max_length=1000)
    audio_nome: str | None = Field(default=None, max_length=255)


class BotaoUpdate(BaseModel):
    rotulo: str | None = Field(default=None, min_length=1, max_length=60)
    significado: str | None = None
    imagem_url: str | None = None
    audio_url: str | None = None
    audio_nome: str | None = None


class CategoriaIn(BaseModel):
    nome: str = Field(min_length=1, max_length=60)
    cor: str | None = Field(default=None, pattern=r"^#[0-9a-fA-F]{6}$")


class DispositivoIn(BaseModel):
    mac: str
    nome: str | None = Field(default=None, max_length=80)
    nome_paciente: str | None = Field(default=None, max_length=120)

    @field_validator("mac")
    @classmethod
    def _mac(cls, v: str) -> str:
        if not _MAC.match(v.strip()):
            raise ValueError("Endereço MAC inválido. Use AA:BB:CC:DD:EE:FF.")
        h = re.sub(r"[^0-9A-Fa-f]", "", v).upper()
        return ":".join(h[i:i + 2] for i in range(0, 12, 2))


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
    uid_local: str = Field(min_length=1, max_length=64)  # id gerado no ESP32 (evita duplicar no reenvio)
    ha_segundos: int = Field(default=0, ge=0, le=60 * 60 * 24 * 30)


class Telemetria(BaseModel):
    bateria_pct: int | None = Field(default=None, ge=0, le=100)
    carregando: bool | None = None
    ip: str | None = Field(default=None, max_length=45)
    firmware: str | None = Field(default=None, max_length=30)
    acionamentos: list[AcionamentoDispositivo] = Field(default_factory=list, max_length=500)
