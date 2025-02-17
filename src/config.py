from pydantic_settings import BaseSettings
from dotenv import find_dotenv, load_dotenv
import os


current_dir = os.path.dirname(os.path.abspath(__file__))

os.chdir(current_dir)

dotenv_path = find_dotenv(".env")
load_dotenv(dotenv_path)


class Settings(BaseSettings): 
    ALGORITHM: str
    SECRET_KEY: str

    TOKEN_EXPIRE: int

    TIME_BLOCK: int

    MAX_ICON_SIZE: int
    MAX_MEDIA_SIZE: int

    PASS_RESET_EXPIRE: int
    PASS_RESET_MONTH: int

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str

    SUPPORT_EMAIL: str

    DB_NAME: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_HOST: str

    REDIS_HOST: str
    REDIS_PORT: int

    X_RAPIDAPI_HOST: str
    X_RAPIDAPI_KEY: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    class ConfigDict:
        env_file = dotenv_path


settings = Settings()
