from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    photoroom_api_key: str
    max_long_edge_px: int = 3000
    host: str = "0.0.0.0"
    port: int = 8080


settings = Settings()
