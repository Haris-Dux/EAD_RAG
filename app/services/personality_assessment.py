

from langchain_core.prompts import ChatPromptTemplate
from weasyprint import HTML
import re


async def generate_personality_assessment_pdf(req, services):

    try:
        Name = req.name
        PersonalityType = req.personality_type
        SelectedInterests = req.selected_interests
        PreferredRole = req.preferred_role
        CareerLevel = req.career_level

        llm = services.llm

        system_prompt = f"""
                   Generate a detailed career consultancy report using ONLY these 5 inputs:
                   Name
                   Personality Type
                   Selected Interests (2 industries)
                   Preferred Role
                   Career Level
                   And 3 Fixed Roles we are offering with Link which are
                   AI Data & Prompt Engineering
                   Generative AI Development
                   AI Brand Strategy & Outreach 
                   
                   Follow this EXACT structure and formatting:
                    
                   Follow this EXACT structure and formatting:
                   # AI Career Consultancy Report  
                   *Name:* {Name}  
                   *Personality Type:* {PersonalityType}  
                   *Selected Interests:* {SelectedInterests[0]}, {SelectedInterests[1]}  
                   *Preferred Role:* {PreferredRole}  
                   *Career Level:* {CareerLevel}
                   
                   1. *How You Shine Naturally:*  (All based on MBTI, 3 Examples are below)
                      - Strategic Visionary: You spot patterns others miss and design systems for the future  
                      - Independent Creator: You do your best work when given space to think deeply  
                      - Precision Engineer: You catch flaws in systems and enjoy optimizing them  
                   
                   
                   2. *Your Superpowers at Work:*  (All based on MBTI, 3 Examples are below)
                      - Dominant Strength: Long-term problem solving (You imagine what could be)  
                      - Supporting Strength: Logical decision-making (You weigh options carefully)  
                      - Growth Area: Adapting to rapid changes (Practice breaking big goals into small steps)  
                   
                   
                   3. *Your Career Personality Type:* {PersonalityType}  (All based on MBTI, 3 Examples are below)
                      - Thrives in: Structured innovation roles  
                      - Best work environment: Autonomous with clear goals  
                      - Ideal challenges: Complex problems needing elegant solutions  
                   
                   
                   4. *Cognitive Functions:*  (All based on MBTI)
                      - Dominant: [Dominant Function]  
                      - Supporting: [Supporting Function]  
                      - Inferior/Avoiding: [Avoiding Function]
                   """

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}")
            ]
        )

        rag_chain = prompt | llm
       
        llm_res = rag_chain.invoke(
            {"input": "Generate a detailed career consultancy report"})
        raw = llm_res.content


        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Personality Assessment Report</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');

        body {{
            font-family: 'Roboto', sans-serif;
            margin: 40px;
            line-height: 1.6;
            color: #000;
        }}
        h1 {{
            text-align: center;
            font-size: 26px;
            margin-bottom: 40px;
        }}
        .info-table {{
            width: 100%;
            margin-bottom: 30px;
        }}
        .info-table td {{
            padding: 5px 10px;
            vertical-align: top;
        }}
        .info-table td.label {{
            font-weight: bold;
            width: 220px;
        }}
        .section-title {{
            font-weight: bold;
            font-size: 18px;
            margin-top: 25px;
        }}
        .section-content {{
            margin-top: 8px;
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>

    <h1>Personality Assessment Report</h1>
"""


        cleaned_result = raw.strip()
        
        
        sections = re.split(r"\n\n(?=\d+\.\s\*)", cleaned_result)
        
        
        for sec in sections:
            if not sec.strip():
                continue
            lines = sec.strip().split('\n', 1)
            if len(lines) == 2:
                heading_line = lines[0].strip()
                content = lines[1].strip().replace('\n', '<br>')
            else:
                heading_line = lines[0].strip()
                content = ""
        
            html_content += f"""
             </body>
            <div class="section-title">{heading_line}</div>
            <div class="section-content">{content}</div>
             </html>
            """


     


        pdf_file_path = f"{Name}_Personality_Assessment.pdf"
        HTML(string=html_content).write_pdf(pdf_file_path)
        return pdf_file_path

    except Exception as error:
        raise error

    finally:
        pass
