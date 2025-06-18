

from langchain_core.prompts import ChatPromptTemplate
from weasyprint import HTML
import re
import json
import base64
from io import BytesIO


async def generate_personality_assessment_pdf(req, services):

    try:
        Name = req.name
        PersonalityType = req.personality_type
        SelectedInterests = req.selected_interests
        PreferredRole = req.preferred_role
        CareerLevel = req.career_level

        llm = services.llm

        system_prompt = (
            "Generate a detailed career consultancy report using ONLY these 5 inputs:.\n\n"
            "- Name: {name}\n"
            "- Personality Type (use descriptive term, not 4-letter MBTI code): {personality_type}\n"
            "- Selected Interests (2 industries): {selected_interests}\n"
            "- Preferred Role: {preferred_role}\n"
            "- Career Level: {career_level}\n\n"
            "Also 3 fixed roles we are offering:\n"
            "1. AI Data & Prompt Engineering\n"
            "2. Generative AI Development\n"
            "3. AI Brand Strategy & Outreach\n\n"
            "⚠️ Respond ONLY in valid JSON format (no markdown, no triple backticks).\n\n"
            "⚠️ DO NOT repeat the examples. Generate fresh, personalized content using the same structure.\n\n"
            "Here are EXAMPLES to guide the structure and tone (DO NOT COPY them):\n\n"
            "1. *How You Shine Naturally:* (All based on MBTI, 3 Examples are below)\n"
            "   - Strategic Visionary: You spot patterns others miss and design systems for the future\n"
            "   - Independent Creator: You do your best work when given space to think deeply\n"
            "   - Precision Engineer: You catch flaws in systems and enjoy optimizing them\n\n"
            "2. *Your Superpowers at Work:* (All based on MBTI, 3 Examples are below)\n"
            "   - Dominant Strength: Long-term problem solving (You imagine what could be)\n"
            "   - Supporting Strength: Logical decision-making (You weigh options carefully)\n"
            "   - Growth Area: Adapting to rapid changes (Practice breaking big goals into small steps)\n\n"
            "3. *Your Career Personality Type:* [Personality Type] (All based on MBTI, 3 Examples are below)\n"
            "   - Thrives in: Structured innovation roles\n"
            "   - Best work environment: Autonomous with clear goals\n"
            "   - Ideal challenges: Complex problems needing elegant solutions\n\n"
            "4. *Cognitive Functions:*  (All based on MBTI)\n"
            "   - Dominant: [Dominant Function]\n"  
            "   - Supporting: [Supporting Function]\n"  
            "   - Inferior/Avoiding: [Avoiding Function]\n\n"  

            "Format:\n"
            "{{\n"
            "  \"personalityAssessment\": {{\n"
            "    \"HowYouShineNaturally\": {{\n"
            "      \"StrategicVisionary\": \"\",\n"
            "      \"IndependentCreator\": \"\",\n"
            "      \"PrecisionEngineer\": \"\"\n"
            "    }},\n"
            "    \"YourSuperpowersatWork\": {{\n"
            "      \"DominantStrength\": \"\",\n"
            "      \"SupportingStrength\": \"\",\n"
            "      \"GrowthArea\": \"\"\n"
            "    }},\n"
            "    \"CareerPersonality\": {{\n"
            "      \"Type\": \"\",\n"
            "      \"ThrivesIn\": \"\",\n"
            "      \"BestEnvironment\": \"\",\n"
            "      \"IdealChallenges\": \"\"\n"
            "    }},\n"
            "    \"CognitiveFunctions\": {{\n"
            "      \"Dominant\": \"\",\n"
            "      \"Supporting\": \"\",\n"
            "      \"Inferior/Avoiding\": \"\"\n"
            "    }}\n"
            "  }},\n"
            "  \"AICareerRecommendationforPhase1\": {{\n"
            "    \"PrimaryRole\": \"<[Preferred Role]>\",\n"
            "    \"BestFitFor\": \"<[Role-specific strength]\",\n"
            "    \"AlternativeRole\": \"<[Alternative Role]  (Based on MBTI, if different than suggested)>\",\n"
            "    \"ConsiderIfYouPrefer\": \"<[Alternative strength]>\"\n"
            "  }},\n"
            "  \"10TEDTalks\": [\n"
            "    \"How AI is Revolutionizing <Industry1>\",\n"
            "    \"The Future of <Industry2> using AI\",\n"
            "    \"<[Industry1-specific talk]>\",\n"
            "    \"<Talk 4>\",\n"
            "    \"<Talk 5>\",\n"
            "    \"<Talk 6>\",\n"
            "    \"<Talk 7>\",\n"
            "    \"<Talk 8>\",\n"
            "    \"<Talk 9>\",\n"
            "    \"<Talk 10>\"\n"
            "  ],\n"
            "  \"10ProfessionalInterviews\": [\n"
            "    \"<Industry1> AI Consultant\",\n"
            "    \"<Industry2> Solutions Architect\",\n"
            "    \"<Interview 3>\",\n"
            "    \"<Interview 4>\",\n"
            "    \"<Interview 5>\",\n"
            "    \"<Interview 6>\",\n"
            "    \"<Interview 7>\",\n"
            "    \"<Interview 8>\",\n"
            "    \"<Interview 9>\",\n"
            "    \"<Interview 10>\"\n"
            "  ],\n"
            "  \"GuidedIndustryAIProjects\": [\n"
            "    \"<Industry1>: <Project 1>\",\n"
            "    \"<Industry2>: <Project 2>\",\n"
            "    \"<Industry1>: <Project 1>\",\n"
            "    \"<Industry2>: <Project 2>\",\n"
            "    \"<Industry1>: <Project 1>\",\n"
            "    \"<Industry2>: <Project 2>\",\n"
            "    \"<Industry1>: <Project 1>\",\n"
            "    \"<Industry2>: <Project 2>\",\n"
            "  ],\n"
            "  \"PersonalBranding\": {{\n"
            "    \"LinkedInOptimizationGuide\": \"<Short optimization guide>\",\n"
            "    \"PortfolioBuildingTemplates\": [\n"
            "      \"Project Showcase Template\",\n"
            "      \"Case Study Template\",\n"
            "      \"Personal Website Template\"\n"
            "    ]\n"
            "  }}\n"
            "}}\n\n"
            "Rules:\n"
            "Auto-generate ALL bracketed content ([Dominant Function], [Project1], etc.) based on:\n"
            "Standard MBTI/personality frameworks\n"
            "The 2 selected industries\n"
            "The preferred role\n"
            "Never add/remove sections - maintain this exact structure\n"
            "Keep tone professional yet encouraging\n"
            "Key Features:\n"
            "✅ Auto-populates cognitive functions (INTP → Introverted Thinking). Also don’t use 4 Letter code or MBTI  but use Personality word for MBTI\n"
            "✅ Generates industry-specific TED Talks and projects\n"
            "✅ Maintains your exact formatting with emojis and sections\n"
            "Context:\n"
            '{{context}}'
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}")
            ]
        )

        rag_chain = prompt | llm

        llm_res = rag_chain.invoke(
            {"input": "Generate a detailed career consultancy report",
             "name": Name,
             "personality_type": PersonalityType,
             "selected_interests": [SelectedInterests[0],SelectedInterests[1]],
             "preferred_role": PreferredRole,
             "career_level": CareerLevel,
             })
        raw = llm_res.content
        cleaned = re.sub(r"^```json\s*|\s*```$", "",
                         raw.strip(), flags=re.DOTALL)
        cleaned = cleaned.strip()
        extracted_data = json.loads(cleaned)


        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Personality Assessment</title>
<style>
    body {{
        font-family: Arial, sans-serif;
        line-height: 1.6;
        padding: 40px;
        color: #333;
    }}
    h1, h2 {{
        color: #2c3e50;
    }}
    section {{
        margin-bottom: 30px;
    }}
    ul {{
        padding-left: 20px;
    }}
    .section-title {{
        margin-bottom: 10px;
        border-bottom: 2px solid #3498db;
        padding-bottom: 5px;
    }}
</style>
</head>
<body>
<h1>Personality Assessment Report</h1>

<section>
    <h2 class="section-title">🌟 How You Shine Naturally</h2>
    <ul>
        {''.join(f'<li><strong>{key}:</strong> {value}</li>' for key, value in extracted_data['personalityAssessment']['HowYouShineNaturally'].items())}
    </ul>
</section>

<section>
    <h2 class="section-title">🦸 Your Superpowers at Work</h2>
    <ul>
        {''.join(f'<li><strong>{key}:</strong> {value}</li>' for key, value in extracted_data['personalityAssessment']['YourSuperpowersatWork'].items())}
    </ul>
</section>

<section>
    <h2 class="section-title">💼 Your Career Personality Type</h2>
    <ul>
        {''.join(f'<li><strong>{key}:</strong> {value}</li>' for key, value in extracted_data['personalityAssessment']['CareerPersonality'].items())}
    </ul>
</section>

<section>
    <h2 class="section-title">🧠 Cognitive Functions</h2>
    <ul>
        {''.join(f'<li><strong>{key}:</strong> {value}</li>' for key, value in extracted_data['personalityAssessment']['CognitiveFunctions'].items())}
    </ul>
</section>

<section>
    <h2 class="section-title">🎯 Primary Role</h2>
    <ul>
        <li><strong>Role:</strong> {extracted_data['AICareerRecommendationforPhase1']['PrimaryRole']}</li>
        <li><strong>Best Fit For:</strong> {extracted_data['AICareerRecommendationforPhase1']['BestFitFor']}</li>
    </ul>
</section>

<section>
    <h2 class="section-title">🛠 Alternative Role</h2>
    <ul>
        <li><strong>Role:</strong> {extracted_data['AICareerRecommendationforPhase1']['AlternativeRole']}</li>
        <li><strong>Consider If You Prefer:</strong> {extracted_data['AICareerRecommendationforPhase1']['ConsiderIfYouPrefer']}</li>
    </ul>
</section>

<section>
    <h2 class="section-title">🎤 Recommended TED Talks</h2>
    <ul>
        {''.join(f'<li>{item}</li>' for item in extracted_data['10TEDTalks'])}
    </ul>
</section>

<section>
    <h2 class="section-title">👥 Target Interviews</h2>
    <ul>
        {''.join(f'<li>{item}</li>' for item in extracted_data['10ProfessionalInterviews'])}
    </ul>
</section>

<section>
    <h2 class="section-title">🚀 Guided Projects</h2>
    <ul>
        {''.join(f'<li>{item}</li>' for item in extracted_data['GuidedIndustryAIProjects'])}
    </ul>
</section>

<section>
    <h2 class="section-title">📌 Personal Branding Tips</h2>
    <h3>LinkedIn</h3>
    <p>{extracted_data['PersonalBranding']['LinkedInOptimizationGuide']}</p>
    <h3>Portfolio Templates</h3>
    <ul>
        {''.join(f'<li>{item}</li>' for item in extracted_data['PersonalBranding']['PortfolioBuildingTemplates'])}
    </ul>
</section>
</body>
</html>
"""


        with BytesIO() as pdf_buffer:
             HTML(string=html_content).write_pdf(pdf_buffer)
             pdf_data = pdf_buffer.getvalue()
             pdf_base64 = base64.b64encode(pdf_data).decode("utf-8")

        return {
            "file_name": f"{Name}_Personality_Assessment.pdf",
            "pdf_base64": pdf_base64,
            "roles":extracted_data['AICareerRecommendationforPhase1']
        }

    except Exception as error:
        raise error

    finally:
        pass
