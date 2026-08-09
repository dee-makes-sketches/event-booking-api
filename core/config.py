from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url:str

    secret_key:SecretStr
    access_token_expire_minutes:int = 30
    algorithm:str = "HS256"


settings = Settings()

