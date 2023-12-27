from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sectors_to_validate: int = 10


settings = Settings()