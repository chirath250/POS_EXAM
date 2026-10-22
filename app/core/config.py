from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pos_db"
    echo_sql: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
