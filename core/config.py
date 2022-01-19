from pydantic import BaseSettings


class Settings(BaseSettings):
    STR_MAX_LENGTH: int = 50
    PASSWORD_REGEX: str = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{4,50}$'

    SERVER_HOST: str = 'http://localhost:8000'
    SERVER_DEVICES: tuple = ('web', 'mobile')

    DATABASE_URL: str
    
    REDIS_URL: str
    REDIS_PASSWORD: str
    REDIS_PORT: str

    SMTP_SERVER: str = 'smtp.gmail.com'
    SMTP_SERVER_PORT: int = 465

    EMAIL_FROM: str = 'test.amirhosss@gmail.com'
    EMAIL_FROM_NAME: str = 'Amirhosss'
    EMAIL_FROM_PASSWORD: str
    
    EMAIL_TEMPLATE_DIR: str = 'email-templates'

    HTTP_BEARER_AUTO_ERROR: bool = False

    JWT_TOKEN_ALGORITHM: str = 'RS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 5

    DEFAULT_LIMITATION: int = 10
    USERS_EXPIRATION_TTL: int = 1800
    USER_COUNTER_RESET_SECONDS: int = 2_592_000


    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()