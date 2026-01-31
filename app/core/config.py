from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str 
    app_env: str = "development"
    debug: bool = False
    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="forbid"
    )

setting = Settings()

