
from app.core.config import Config
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq




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


        #    self.llm = ChatGroq(
#             model="meta-llama/llama-4-scout-17b-16e-instruct",
#             temperature=0.3,
#             api_key=Config.GROQ_API_KEY
#         )
#         cleaned = re.sub(r"(?:```json|```|<think>.*?</think>)", "", result, flags=re.DOTALL).strip() 