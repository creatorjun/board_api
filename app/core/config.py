from pydantic import computed_field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database settings (한 줄씩 읽어오도록 필드 정의)
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    # Naver Ad API settings
    NAVER_AD_API_KEY: str
    NAVER_AD_SECRET_KEY: str
    NAVER_AD_CUSTOMER_ID: str | None = None

    # Naver Social Login settings
    NAVER_CLIENT_ID: str
    NAVER_CLIENT_SECRET: str
    
    # Kakao Social Login settings
    KAKAO_CLIENT_SECRET: str

    # JWT settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # 위 필드들을 조합하여 DATABASE_URL을 계산
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

settings = Settings()