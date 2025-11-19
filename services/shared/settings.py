from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_ROOT_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    print(f"Carregando variaveis de ambiente de: {REPO_ROOT_DIR / '.env'}")

    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    rabbitmq_user: str
    rabbitmq_pass: str
    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_vhost: str

settings = Settings()
