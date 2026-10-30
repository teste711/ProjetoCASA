"""Armazenamento e validação de mídia: imagens viram JPEG 240x240 (telas do ESP32); áudio MP3/WAV."""
import hashlib
import io
import uuid
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from .config import settings
from .deps import erro

RAIZ = Path(settings.upload_dir)


def garantir_pasta() -> None:
    RAIZ.mkdir(parents=True, exist_ok=True)


def caminho(arquivo: str) -> Path:
    p = (RAIZ / arquivo).resolve()
    if RAIZ.resolve() not in p.parents:  # defesa contra path traversal
        raise erro(400, "arquivo_invalido", "Caminho de arquivo inválido.")
    return p


def abrir_existente(arquivo: str) -> Path:
    """Caminho do arquivo ou 404 (ex.: pasta uploads apagada ou servidor iniciado de outra pasta)."""
    p = caminho(arquivo)
    if not p.is_file():
        raise erro(404, "arquivo_ausente", "O arquivo não foi encontrado no servidor. Envie-o novamente.")
    return p


def detectar_audio(dados: bytes) -> tuple[str, str] | None:
    """Valida pelos bytes (não pelo nome/Content-Type enviados pelo cliente)."""
    if dados[:4] == b"RIFF" and dados[8:12] == b"WAVE":
        return "audio/wav", ".wav"
    if dados[:3] == b"ID3" or (len(dados) > 2 and dados[0] == 0xFF and (dados[1] & 0xE0) == 0xE0):
        return "audio/mpeg", ".mp3"
    return None


def processar_imagem(dados: bytes) -> bytes:
    try:
        with Image.open(io.BytesIO(dados)) as im:
            if im.format not in {"PNG", "JPEG", "WEBP"}:
                raise erro(415, "formato_nao_suportado", "Use imagens PNG, JPEG ou WEBP.")
            if im.width * im.height > 50_000_000:  # recusa antes de decodificar (evita estourar a memória)
                raise erro(413, "imagem_grande", "A imagem tem dimensões grandes demais. Use uma menor.")
            im = ImageOps.exif_transpose(im)
            if im.mode in ("RGBA", "LA", "P"):
                im = im.convert("RGBA")
                fundo = Image.new("RGB", im.size, (255, 255, 255))
                fundo.paste(im, mask=im.split()[-1])
                im = fundo
            else:
                im = im.convert("RGB")
            lado = settings.imagem_lado_px
            im = ImageOps.fit(im, (lado, lado), Image.LANCZOS)
            saida = io.BytesIO()
            im.save(saida, format="JPEG", quality=85, optimize=True, progressive=False)  # baseline: o decodificador do ESP32 não lê progressivo
            return saida.getvalue()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise erro(415, "imagem_invalida", "O arquivo enviado não é uma imagem válida.")


def salvar(dados: bytes, extensao: str) -> tuple[str, str]:
    garantir_pasta()
    nome = f"{uuid.uuid4().hex}{extensao}"
    caminho(nome).write_bytes(dados)
    return nome, hashlib.sha256(dados).hexdigest()


def remover(arquivo: str) -> None:
    try:
        caminho(arquivo).unlink(missing_ok=True)
    except Exception:
        pass
