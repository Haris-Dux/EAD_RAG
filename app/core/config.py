import os
from dotenv import load_dotenv
load_dotenv()


class Config:

    GEMINI_API_KEY = os.getenv("GEMNI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPEN_AI_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    @classmethod
    def validate(cls):

        required_vars = {
            "GEMNI_API_KEY": cls.GEMINI_API_KEY,
            "OPEN_AI_KEY": cls.OPENAI_API_KEY,
            "JWT_SECRET_KEY":cls.JWT_SECRET_KEY
        }

        missing = [key for key, value in required_vars.items() if not value]
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}")


