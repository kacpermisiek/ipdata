from pydantic import AnyHttpUrl, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_dsn: SecretStr = SecretStr("postgresql://alice:xyz@localhost:5432/ipdata")
    ip_stack_url: AnyHttpUrl = AnyHttpUrl("https://api.ipstack.com")
    ip_stack_access_key: SecretStr = SecretStr("change_me")


settings = Settings()
