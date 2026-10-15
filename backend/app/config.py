from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    firebase_credentials: str = ""  # vazio = credenciais padrão do Google (GOOGLE_APPLICATION_CREDENTIALS)
    cors_origins: str = "http://localhost:3000"
    require_email_verified: bool = True
    max_categorias: int = 3
    max_botoes_por_categoria: int = 5


settings = Settings()
