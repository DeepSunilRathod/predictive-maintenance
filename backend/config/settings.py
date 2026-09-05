"""
Application settings, loaded from environment variables (.env).
Never hard-code credentials here.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from urllib.parse import quote_plus


class Settings(BaseSettings):
    # Database
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=3306, alias="DB_PORT")
    db_user: str = Field(default="root", alias="DB_USER")
    db_password: str = Field(default="", alias="DB_PASSWORD")
    db_name: str = Field(default="predictive_maintenance", alias="DB_NAME")

    # App
    motor_id: str = Field(default="MOTOR-001", alias="MOTOR_ID")
    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")
    api_key: str = Field(default="", alias="DEVICE_API_KEY")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Demo mode default (can also be toggled at runtime via /api/settings)
    demo_mode_default: bool = Field(default=True, alias="DEMO_MODE_DEFAULT")

    @property
    def database_url(self) -> str:
        password = quote_plus(self.db_password)
        return (
        f"mysql+pymysql://{self.db_user}:{password}"
        f"@{self.db_host}:{self.db_port}/{self.db_name}"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        populate_by_name = True


settings = Settings()
