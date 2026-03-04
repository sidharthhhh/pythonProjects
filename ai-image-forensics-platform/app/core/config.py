from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENVIRONMENT: str = "production"
    REDIS_URL: str = "redis://localhost:6379/0"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_IMAGE_FORMATS: list[str] = ["jpeg", "jpg", "png", "webp", "tiff", "bmp", "heic"]
    
    # Model Paths
    AI_CLASSIFIER_MODEL_PATH: str = "/models/ai_classifier.pt"
    
    class Config:
        env_file = ".env"

settings = Settings()
