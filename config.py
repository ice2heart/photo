from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    host: str
    identity: str
    psk: str

    model_config = SettingsConfigDict(env_file=".env")