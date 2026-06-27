from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "K8s Secret Manager"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "root"
    DB_NAME: str = "ksm_secret_manager"

    @property
    def db_url(self) -> str:
        return f"mysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    JWT_SECRET: str = "change-this-to-a-random-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480

    AES_SECRET_KEY: str = "change-this-to-a-32-byte-key!"
    AES_SECRET_IV: str = "1234567890abcdef"

    K8S_SDK_TIMEOUT: int = 10
    SECRET_CACHE_TTL: int = 300

    AUTH_SERVICE_PORT: int = 8001
    ENV_SERVICE_PORT: int = 8002
    SECRET_SERVICE_PORT: int = 8003
    TOOLBOX_SERVICE_PORT: int = 8004
    GATEWAY_PORT: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
