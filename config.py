from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APPLICATION_VERSION: str
    TEST_MODE: bool
    
    model_config = SettingsConfigDict(env_file=".env")
    