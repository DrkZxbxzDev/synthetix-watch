from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Synthetix Watch API"
    DATABASE_URL: str = "sqlite+aiosqlite:///./synthetix_watch.db"
    SCREENSHOT_DIR: str = "screenshots"

    class Config:
        env_file = ".env"

settings = Settings()