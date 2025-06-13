
from app.core.config import Config
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI




class servicesContainer:
    def __init__(self):
        self.embeddings = None
        self.llm = None

    def initialize_services(self):
      
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=Config.GEMINI_API_KEY
        )
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-preview-05-20",
            temperature=0.1,
            max_retries=2,
            google_api_key=Config.GEMINI_API_KEY
        )