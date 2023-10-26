from pydantic import BaseSettings


class Settings(BaseSettings):
    sectors_to_validate = 10


settings = Settings()