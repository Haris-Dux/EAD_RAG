import os
from dotenv import load_dotenv
load_dotenv()


class Config:

    GEMINI_API_KEY = os.getenv("GEMNI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    DB_SERVER = os.getenv("DB_SERVER")
    DB_DATABASE = os.getenv("DB_DATABASE")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH")

    @classmethod
    def validate(cls):

        required_vars = {
            "GEMNI_API_KEY": cls.GEMINI_API_KEY,
            "GROQ_API_KEY": cls.GROQ_API_KEY,
            "JWT_SECRET_KEY":cls.JWT_SECRET_KEY,
            "DB_SERVER": cls.DB_SERVER,
            "DB_DATABASE": cls.DB_DATABASE,
            "DB_USER": cls.DB_USER,
            "DB_PASSWORD": cls.DB_PASSWORD,
            "CHROMA_DB_PATH": cls.CHROMA_DB_PATH
        }

        missing = [key for key, value in required_vars.items() if not value]
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}")


