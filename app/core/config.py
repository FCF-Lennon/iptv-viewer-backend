from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str 
    app_env: str = Field(default="development", env="APP_ENV")
    debug: bool = False
    database_url: str
    jwt_secret: str
    fernet_key: str  # clave independiente para cifrado de credenciales Xtream

    xtream_user_agent: str = "SmartShesPro/1.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # ignorar variables de entorno del sistema
    )

setting = Settings()

