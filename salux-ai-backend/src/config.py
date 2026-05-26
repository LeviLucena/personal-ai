from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    host: str = "0.0.0.0"
    port: int = 8000
    telegram_bot_token: str = ""
    database_url: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
BASE_DIR = Path(__file__).resolve().parent.parent
