
import pymssql
from app.core.config import Config

def get_db_connection():
    try:
        conn = pymssql.connect(Config.DB_SERVER,Config.DB_USER,Config.DB_PASSWORD,Config.DB_DATABASE,)
        print("✅ Success: MSSQL connected.")
        return conn
    except pymssql.Error as error:
        raise Exception(f"Database connection failed: {error}")
     