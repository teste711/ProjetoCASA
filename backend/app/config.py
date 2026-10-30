from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    firebase_credentials: str = ""  # vazio = credenciais padrão do Google (GOOGLE_APPLICATION_CREDENTIALS)
    # URL do Realtime Database (console > Realtime Database). Necessária para o fluxo do IoT (sinal/flag).
    firebase_database_url: str = ""   # ex.: https://SEU-PROJETO-default-rtdb.firebaseio.com
    cors_origins: str = "http://localhost:3000"
    require_email_verified: bool = True
    max_categorias: int = 3
    max_botoes_por_categoria: int = 5
    bateria_baixa_pct: int = 20
    device_offline_minutos: int = 10
    timezone: str = "America/Sao_Paulo"

    # Segredo usado no hash dos códigos de e-mail. TROQUE em produção (openssl rand -hex 32)
    secret_key: str = "dev-troque-esta-chave"

    # Cadastro com código por e-mail
    codigo_validade_minutos: int = 15
    codigo_max_tentativas: int = 5
    codigo_reenvio_segundos: int = 60

    # SMTP. SMTP_HOST vazio = modo desenvolvimento (NENHUM e-mail é enviado; o código aparece no terminal).
    # SMTP_SERVER também é aceito (nome usado em outros trechos do projeto).
    smtp_host: str = Field("", validation_alias=AliasChoices("smtp_host", "smtp_server"))
    smtp_port: int = 587          # 587 = STARTTLS · 465 = SSL direto
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""           # vazio = usa o próprio SMTP_USER (o Gmail exige o mesmo endereço)
    smtp_tls: bool = True         # STARTTLS (porta 587)
    smtp_ssl: bool = False        # SSL direto; a porta 465 já ativa isto sozinha
    smtp_timeout: int = 15

    # Fluxo do IoT: app → API → Firestore (base64) + sinal no Realtime Database → dispositivo
    iot_max_pendentes: int = 20            # itens aguardando o aparelho (15 pictogramas + folga)
    iot_pendente_expira_horas: int = 168   # item que o aparelho nunca buscou é descartado após 7 dias
    iot_concluido_expira_horas: int = 24   # sinal "concluído" some do Realtime Database após 24 h
    iot_max_audio_kb: int = 500            # áudio bruto; em base64 precisa caber no limite de 1 MiB do Firestore
    iot_max_base64_bytes: int = 900_000
    iot_max_tentativas: int = 5

    # Mídia (imagens/áudios dos botões do site) — gravada em disco no servidor
    upload_dir: str = "./uploads"
    max_imagem_mb: int = 5
    max_audio_mb: int = 5
    imagem_lado_px: int = 240    # telas TFT ST7789 do aparelho
    max_midias_por_usuario: int = 200


settings = Settings()
