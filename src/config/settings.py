from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PORT: int = 8000
    DB_HOST: str = "localhost"
    DB_USER: str = ""
    DB_PASS: str = ""
    DB_NAME: str = "inventory_system"
    JWT_SECRET: str
    COOKIE_SECRET: str

    class Config:
        env_file = ".env"

settings = Settings()
