from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ' extra="ignore" 'define que as variaveis que
    # não são importadas do .env devem ser ignoradas
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACESS_TOKEN_EXPIRE_MINUTES: int
