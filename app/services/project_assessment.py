
from fastapi import HTTPException
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
import json
import re
from app.utils.common import normalizeString


async def generate_project_assessment(req, services,db):

    try:
        project_title = req.project_title
        normalize_title = normalizeString(project_title)
        assessment_title = req.assessment_title
        embeddings = services.embeddings
        vector_store = Chroma(
            embedding_function=embeddings,
            persist_directory="./chroma_db",
            collection_name=normalize_title
        )
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        docs = retriever.invoke(normalize_title) 
        if not docs:
            raise HTTPException(
                status_code=404,
                detail=f"No data available for project '{project_title}'. Please check the role or upload data first."
            )
        llm = services.llm

        system_prompt = (
    f"You are an expert educator and exam content creator.\n"
    f"Your task is to generate **5 challenging multiple-choice questions (MCQs)** for an assessment titled: \"{assessment_title}\".\n\n"
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

        return {
            "questions":questions,
        }

    except Exception as error:
             raise error

    finally:
        pass

