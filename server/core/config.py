from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    DATABASE_URL: str
    DEBUG: bool = False
    OPENAI_API_KEY: str
    ALLOW_ORIGINS: str = ""

    @field_validator("ALLOW_ORIGINS")
    def parse_allowed_origins(cls, v: str) -> List[str]:
        return v.split(",") if v else []


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

