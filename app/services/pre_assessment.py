import os
import tempfile
from fastapi import UploadFile,HTTPException
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
import chromadb
from chromadb.config import Settings
from datetime import datetime
import json
import re
from app.utils.common import normalizeString
from app.core.config import Config



async def update_preassessment_data(services, file: UploadFile, roleName: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:

        #  READ FILE
        loader = PyPDFLoader(tmp_path) 
        data = loader.load()
        name = normalizeString(roleName)

    # SPLIT TEXT
        textSplitter = RecursiveCharacterTextSplitter(chunk_size=800)
        docs = textSplitter.split_documents(data)

    #  EMBEDDING
        embeddings = services.embeddings

        client = chromadb.PersistentClient(path=Config.CHROMA_DB_PATH)
        existing_collections = client.list_collections()
        if name in existing_collections:
            print(f"Found Collection /{name}")
            client.delete_collection(name=name)
            deleted = print("deleting existing")
            print(f"Collection {name} deleted: {deleted}")

        # existing_collections_number = client.count_collections()
        # print(f"Existing collections Before resseting: {existing_collections_number}")
        # client.reset()
        # existing_collections_number = client.count_collections()
        # print(f"Existing collections After: {existing_collections_number}")
        #  existing_collections = client.list_collections()

        vector_store = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory=Config.CHROMA_DB_PATH,
            collection_name=name
        )

        return str(vector_store)

    except Exception as error:
     raise error

    finally:
        os.remove(tmp_path)


async def generate_preassessment_for_role(req, services,db):

    try:
        role = normalizeString(req.role)
        print(role)
        pre_assessment_id = req.pre_assessment_id
        embeddings = services.embeddings
        vector_store = Chroma(
            embedding_function=embeddings,
            persist_directory=Config.CHROMA_DB_PATH,
            collection_name=role
        )
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        docs = retriever.invoke(role) 
        if not docs:
            raise HTTPException(
                status_code=404,
                detail=f"No data available for role '{req.role}'. Please check the role or upload data first."
            )
        llm = services.llm

        system_prompt = (
    f"You are an expert educator and exam content creator.\n"
    f"Your task is to generate **5 challenging multiple-choice questions (MCQs)** for an assessment titled: \"{role}\".\n\n"
    "The questions must be deeply relevant to both the **title** and the **provided content**, testing deep understanding rather than rote recall.\n\n"
    "Guidelines:\n"
    "- Each question must have **4 options** (A, B, C, D).\n"
    "- Only **one option should be correct**.\n"
    "- Ensure the distractors (wrong options) are plausible but clearly incorrect upon careful thought.\n"
    "- Vary the question type: some factual, some conceptual, some inferential.\n"
    "- Use formal academic language and ensure the questions match the tone and depth of the input text.\n\n"
    "Respond ONLY in valid JSON format (no markdown formatting or triple backticks).\n\n"
    "Format:\n"
    "{{\n"
    "  \"questions\": [\n"
    "    {{\n"
    "      \"id\": 1,\n"
    "      \"question\": \"<The question text>\",\n"
    "      \"options\": {{\n"
    "        \"A\": \"<Option A>\",\n"
    "        \"B\": \"<Option B>\",\n"
    "        \"C\": \"<Option C>\",\n"
    "        \"D\": \"<Option D>\"\n"
    "      }}\n"
    "    }},\n"
    "    ... (4 more questions)\n"
    "  ],\n"
    "  \"answers\": [\n"
    "    {{ \"id\": 1, \"correctAnswer\": \"C\" }},\n"
    "    {{ \"id\": 2, \"correctAnswer\": \"A\" }},\n"
    "    {{ \"id\": 3, \"correctAnswer\": \"D\" }},\n"
    "    {{ \"id\": 4, \"correctAnswer\": \"B\" }},\n"
    "    {{ \"id\": 5, \"correctAnswer\": \"C\" }}\n"
    "  ]\n"
    "}}\n\n"
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
        llm_res = rag_chain.invoke(
            {"input": "Generate 5 multiple choice questions from the above context."})
        result = llm_res["answer"]
        cleaned = re.sub(r"^```json\s*|\s*```$", "", result.strip(), flags=re.DOTALL)
        response = json.loads(cleaned)
        questions = response["questions"]
        answers = response["answers"]

        # UPDATE DATABASE
        answers_json = json.dumps(answers)
        questions_json = json.dumps(questions)
        cursor = db.cursor()
        cursor.execute("INSERT INTO preAssessmentSubmission VALUES (%s, %s, %s, %s, %s) SELECT SCOPE_IDENTITY()", (pre_assessment_id, 0,answers_json, questions_json, None))
        row = cursor.fetchone()
        assessment_id = int(row[0])
        db.commit()

        return {
            "questions":questions,
            "assessment_submission_id":assessment_id
        }

    except Exception as error:
             raise error

    finally:
        pass


async def create_pre_assessment_submission(req,db):
     try:
         selected_answers = req.answers
         assessment_submission_id = req.assessment_submission_id
         cursor = db.cursor()
         query = "SELECT answers,pre_assessment_id FROM preAssessmentSubmission where id = %s"
         cursor.execute(query,(assessment_submission_id))
         result = cursor.fetchone()
         correct_answers_json, pre_assessment_id = result
         correct_answers = json.loads(correct_answers_json)
         score = 0

         correct_dict = {item['id']: item['correctAnswer'] for item in correct_answers}
         for selected in selected_answers:   
            correct_option = correct_dict.get(selected.id)
            if selected.correctAnswer == correct_option:
                score += 1

         if score >= 3:
               cursor.execute("""
                 UPDATE preAssessmentSubmission 
                 SET is_submitted = %s, submitted_at = %s 
                 WHERE id = %s
             """, (1, datetime.now(), assessment_submission_id))

       
               cursor.execute("""
                UPDATE preAssessmentCompletion 
                SET isCompleted = %s 
                WHERE id = %s
             """, (1, pre_assessment_id))

         db.commit()

         return {"score": score}
     except Exception as error:
        raise error
     finally:
          cursor.close()