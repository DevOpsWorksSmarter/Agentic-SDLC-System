from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/urlshortener"
    redis_url: str = "redis://localhost:6379/0"
    base_url: str = "http://localhost:8000"
    cache_ttl_seconds: int = 86400  # 24h
    rate_limit_per_minute: int = 60
    code_length: int = 7

    class Config:
        env_file = ".env"


settings = Settings()
