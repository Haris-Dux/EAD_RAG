import os
import tempfile
from fastapi import UploadFile

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
import chromadb
from chromadb.config import Settings


async def update_preassessment_data(services, file: UploadFile, roleName: str):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:

        #  READ FILE
        loader = PyPDFLoader(tmp_path)
        data = loader.load()
        name = roleName

    # SPLIT TEXT
        textSplitter = RecursiveCharacterTextSplitter(chunk_size=1000)
        docs = textSplitter.split_documents(data)

    #  EMBEDDING
        embeddings = services.embeddings

        client = chromadb.PersistentClient(path='./chroma_db')
        existing_collections = client.list_collections()
        if name in existing_collections:
            print(f"Found Collection /{name}")
            client.delete_collection(name=name)
            deleted = print("deleting existing")
            print(f"Collection {name} deleted: {deleted}")

    #  client.reset()
    #  existing_collections_number = client.count_collections()
    #  print(f"Existing collections After: {existing_collections_number}")
    #  existing_collections = client.list_collections()

        vector_store = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory="./chroma_db",
            collection_name=name
        )

        return str(vector_store)

    except Exception as error:
        return str(error)

    finally:
        os.remove(tmp_path)


async def generate_preassessment_for_role(req, services):

    try:
        role = req.role
        embeddings = services.embeddings
        vector_store = Chroma(
            embedding_function=embeddings,
            persist_directory="./chroma_db",
            collection_name=role
        )
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        llm = services.llm

        system_prompt = (
            "You are an expert educator and exam content creator.\n"
            "Given the following text, your task is to create **5 challenging multiple-choice questions (MCQs)** "
            "that test **deep understanding**, not just recall.\n\n"
            "Guidelines:\n"
            "- Each question must have **4 options** (A, B, C, D).\n"
            "- Only **one option should be correct**.\n"
            "- Include the **correct answer** after each question.\n"
            "- Ensure the distractors (wrong options) are plausible but clearly incorrect upon careful thought.\n"
            "- Vary the question type: some factual, some conceptual, some inferential.\n"
            "- Use formal academic language and ensure the questions match the tone and depth of the input text.\n\n"
            "Respond in the following format:\n\n"
            "1. Question text?\n"
            "   A. Option A\n"
            "   B. Option B\n"
            "   C. Option C\n"
            "   D. Option D\n"
            "**Answer: C**\n\n"
            "Context:\n"
            "{context}"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}")
            ]
        )

        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        result = rag_chain.invoke(
            {"input": "Generate 5 multiple choice questions from the above context."})

        return str(result["answer"])

    except Exception as error:
        return str(error)
    finally:
        pass
