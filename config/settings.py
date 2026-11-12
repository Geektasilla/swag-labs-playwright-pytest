from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Test settings. Values can be overridden with environment variables or a local .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    standard_user: str = "standard_user"
    locked_out_user: str = "locked_out_user"
    problem_user: str = "problem_user"
    performance_glitch_user: str = "performance_glitch_user"
    error_user: str = "error_user"
    visual_user: str = "visual_user"
    # Public demo password published on the saucedemo.com login page - not a secret.
    password: str = "secret_sauce"


settings = Settings()
