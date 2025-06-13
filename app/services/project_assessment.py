
from fastapi import HTTPException
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
import json
import re
from app.utils.common import normalizeString
from datetime import datetime
from app.core.config import Config



async def generate_assessment_for_project(req, services, db):

    try:
        project_title = req.project_title
        normalize_title = normalizeString(project_title)
        assessment_title = req.assessment_title
        embeddings = services.embeddings
        vector_store = Chroma(
            embedding_function=embeddings,
            persist_directory=Config.CHROMA_DB_PATH,
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
                detail=f"No data available for project '{project_title}'. Please check the project or upload data first."
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
        cleaned = re.sub(r"^```json\s*|\s*```$", "",
                         result.strip(), flags=re.DOTALL)
        response = json.loads(cleaned)
        questions = response["questions"]
        questions_json = json.dumps(questions)
        answers = response["answers"]
        answers_json = json.dumps(answers)

        cursor = db.cursor()
        cursor.execute("INSERT INTO AssessmentSubmission VALUES (%s, %s, %s, %s, %s) SELECT SCOPE_IDENTITY()",
                       (0, answers_json, " ", questions_json, None))
        row = cursor.fetchone()
        assessment_id = int(row[0])
        db.commit()

        return {
            "questions": questions,
            "assessment_submission_id": assessment_id
        }

    except Exception as error:
        raise error

    finally:
        pass


async def evaluate_project_assessment(req, services, db, user):
    try:

        assessment_title = req.assessment_title
        assessment_id = req.assessment_id
        project_title = req.project_title
        assessment_submission_id = req.assessment_submission_id
        dataSpreadsheet = req.deliverables.dataSpreadsheet
        aiCharts = req.deliverables.aiCharts
        dataInsights = req.deliverables.dataInsights
        selected_answers = req.answers
        user_id = user['id']

        # get project vectorized data collection
        normalize_title = normalizeString(project_title)
        embeddings = services.embeddings
        vector_store = Chroma(
            embedding_function=embeddings,
            persist_directory=Config.CHROMA_DB_PATH,
            collection_name=normalize_title
        )
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 1}
        )
        docs = retriever.invoke(normalize_title)
        if not docs:
            raise HTTPException(
                status_code=404,
                detail=f"No data available for project '{project_title}'. Please check the project details or upload data first."
            )
        llm = services.llm

        # get relevent json data for assessment
        with open("./assessment_criteria/assessment_criteria.json") as file:
            data = json.load(file)

        rubricsData = data.get(assessment_title)
        rubrics_string = json.dumps(rubricsData, indent=2)

        # get mcq score
        cursor = db.cursor()
        query = f"""   
              SELECT 
              (SELECT correctAnswers FROM AssessmentSubmission where id = {assessment_submission_id}),
              (SELECT id FROM Students where user_id = {user_id})
"""
        # "SELECT correctAnswers FROM AssessmentSubmission where id = %s"
        cursor.execute(query)
        result = cursor.fetchone()
        correct_answers_json, student_id = result
        correct_answers = json.loads(correct_answers_json)

        mcqScore = 0
        totalMCQ = len(correct_answers)
        correct_dict = {item['id']: item['correctAnswer']
                        for item in correct_answers}
        for selected in selected_answers:
            correct_option = correct_dict.get(selected.id)
            if selected.correctAnswer == correct_option:
                mcqScore += 1

        # merge deliverables data
        deliverables_string = f'Spreadsheet: {dataSpreadsheet}, Charts: {aiCharts}, Insights: {dataInsights}'

        # system prompt to generate evaluation
        system_prompt = (
            "You are an expert assessment evaluator. Your task is to generate a structured JSON report based strictly on the following input data:\n\n"
            "1. Input Data:\n"
            "   - Total MCQ: {total_mcq}\n"
            "   - MCQ Score: {mcq_score}\n"
            "   - Project Requirements (from provided vector data)\n"
            "   - Student Deliverables: {deliverables}\n"
            "   - Assessment Criteria: {assessment_title}\n"
            "   - Rubrics: {rubrics}\n\n"
            "2. Report Output Format:\n"
            "Return the report strictly as a JSON object with the following keys and expected values:\n\n"
            "{{\n"
            "  \"MCQ_Evaluation\": \"string (concise explanation based on MCQ score from Total MCQ and Project Requirements)\",\n"
            "  \"Rubric_Evaluation (Generate Rubric_Evaluation for each criteria in Rubrics based on input data)\": [\n"
            "    {{\n"
            "      \"Criteria\": \"string\",\n"
            "      \"Level\": \"string\",\n"
            "      \"Score\": number\n"
            "    }}\n"
            "  ],\n"
            "  \"Area_for_Improvement\": \"string (brief, to the point suggestion for weak points)\",\n"
            "  \"AI_Opinion\": \"string (brief, forward-looking, objective summary)\"\n"
            "}}\n\n"
            "----\n"
            "Additional Context:\n"
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
            {"input": "Please generate a comprehensive evaluation report based on the provided information.",

             "rubrics": rubrics_string,
             "deliverables": deliverables_string,
             "assessment_title": assessment_title,
             "mcq_score": mcqScore,
             "total_mcq": totalMCQ,
             })
        result = llm_res["answer"]
        cleaned = re.sub(r"^```json\s*|\s*```$", "",
                         result.strip(), flags=re.DOTALL)
        response = json.loads(cleaned)

        # update database
        rubrics = response["Rubric_Evaluation"]
        overallTotal = len(rubrics) * 10 + totalMCQ

        rubricsTotal = 0 
        for i in rubrics:
            rubricsTotal += i["Score"]

        overallScore = mcqScore + rubricsTotal
        cursor.execute("INSERT INTO AssessmentEvaluations VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) SELECT SCOPE_IDENTITY()",
                 (mcqScore, totalMCQ, response["MCQ_Evaluation"], response["Area_for_Improvement"], response["AI_Opinion"], overallTotal, student_id, assessment_id, overallScore, 0, datetime.now(), 1, 1, None, 0, assessment_submission_id ))
        row = cursor.fetchone()
        assessment_evaluation_id = int(row[0])
        
        for rubric in rubrics:       
         cursor.execute("INSERT INTO RubricEvaluations VALUES (%s, %s, %s, %s, %s)",(rubric["Criteria"], rubric["Level"], rubric["Score"], 10, assessment_evaluation_id))
        
        selected_answers_serialized = [
        {"id": ans.id, "correctAnswer": ans.correctAnswer}
         for ans in selected_answers
        ] 

        selected_answers_json = json.dumps(selected_answers_serialized)
        query = "UPDATE AssessmentSubmission SET selectedAnswers = %s, submitted_at = %s WHERE id = %s"
        cursor.execute(query, (selected_answers_json, datetime.now(), assessment_submission_id))
        return response

    except Exception as error:
        db.rollback()
        raise error
    finally:
        db.commit()
        cursor.close()
