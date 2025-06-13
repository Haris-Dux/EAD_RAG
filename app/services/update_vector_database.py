
from fastapi import HTTPException
from app.utils.common import normalizeString
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from pypdf import PdfWriter
import chromadb
import os
import aiohttp
import asyncio
from app.core.config import Config


async def sync_project_files(req,services,db):
    try:
        project_id = req.project_id
        project_title = req.project_title
        normalize_title = normalizeString(project_title)
        cursor = db.cursor()
        query = 'SELECT fileName FROM Lessons WHERE project_id = %s'
        cursor.execute(query,(project_id))
        files = cursor.fetchall()
        if not len(files):
            raise HTTPException(
                status_code=404,
                detail="No files to update for this project"
            )
        
        # DOWNLOAD PDF's
        file_urls = [f[0] for f in files]
        local_files = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i, url in enumerate(file_urls):
                local_name = f"temp_{i}.pdf"
                local_files.append(local_name)
                tasks.append(download_pdf(session,url,local_name))
            await asyncio.gather(*tasks)

        # MERGE PDF's
        merger = PdfWriter()
        for pdf_file in local_files:
            merger.append(pdf_file)

        merged_filename = f"{normalize_title}.pdf"
        with open(merged_filename , "wb") as file:
            merger.write(file)
        merger.close()

        for pdf_file in local_files:
            os.remove(pdf_file)

        # UPDATE CHROMA DB
        loader = PyPDFLoader(merged_filename)
        data = loader.load()

        textSplitter = RecursiveCharacterTextSplitter(chunk_size=800)
        docs = textSplitter.split_documents(data)
        embeddings = services.embeddings
        client = chromadb.PersistentClient(path=Config.CHROMA_DB_PATH)
        existing_collections = client.list_collections()
        if normalize_title in existing_collections:
            print(f"Found Collection /{normalize_title}")
            client.delete_collection(name=normalize_title)
            deleted = print("deleting existing")
            print(f"Collection {normalize_title} deleted: {deleted}")
        else:
            print(f"Collection /{normalize_title} does not exist")

        
        vector_store = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory=Config.CHROMA_DB_PATH,
            collection_name=normalize_title
        )

        return str(vector_store)

    except Exception as error:
        raise error
    finally:
        cursor.close()



# Download a single PDF file
async def download_pdf(session, url, filename):
    async with session.get(url) as response:
        if response.status != 200:
            raise HTTPException(500,f"Failed to download {url}")
        with open(filename, 'wb') as f:
            f.write(await response.read())