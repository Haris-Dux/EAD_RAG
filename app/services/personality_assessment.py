

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
                 # AI Career Consultancy Report  
                 *Name:* [Name]  
                 *Personality Type:* [Personality Type]  
                 *Selected Interests:* [Industry1], [Industry2]  
                 *Preferred Role:* [Preferred Role]  
                 *Career Level:* [Career Level]  
                 
                 
                 ### a) Personality Assessment 
                 1. *How You Shine Naturally:*  (All based on MBTI, 3 Examples are below)
                    - Strategic Visionary: You spot patterns others miss and design systems for the future  
                    - Independent Creator: You do your best work when given space to think deeply  
                    - Precision Engineer: You catch flaws in systems and enjoy optimizing them  
                 
                 
                 2. *Your Superpowers at Work:*  (All based on MBTI, 3 Examples are below)
                    - Dominant Strength: Long-term problem solving (You imagine what could be)  
                    - Supporting Strength: Logical decision-making (You weigh options carefully)  
                    - Growth Area: Adapting to rapid changes (Practice breaking big goals into small steps)  
                 
                 
                 3. *Your Career Personality Type:* [Personality Type]  (All based on MBTI, 3 Examples are below)
                    - Thrives in: Structured innovation roles  
                    - Best work environment: Autonomous with clear goals  
                    - Ideal challenges: Complex problems needing elegant solutions  
                 
                 
                 4. *Cognitive Functions:*  (All based on MBTI)
                    - Dominant: [Dominant Function]  
                    - Supporting: [Supporting Function]  
                    - Inferior/Avoiding: [Avoiding Function]  
                 
                 
                 ### What you should do NEXT  
                 *1)* AI Career Recommendation for Phase 1**  
                 *Primary Role:* [Preferred Role]  
                 - Best Fit For: [Role-specific strength]  
                 - Self-Guided Booklet: [Role] Development with [Link]  
                 
                 
                 *Alternative Role:* [Alternative Role]  (Based on MBTI, if different than suggested)
                 - Consider If You Prefer: [Alternative strength]  
                 - Self-Guided Booklet: [Alternative] with [Link]  
                 
                 
                 *2)* 10 TED Talks (on Selected Industries):**  
                 1. "How AI is Revolutionizing [Industry1]"  
                 2. "The Future of [Industry2] using AI"  
                 3. [Industry1-specific talk]  
                 ...  
                 
                 
                 *3)* 10 Professional Interviews:**  
                 1. [Industry1] AI Consultant  
                 2. [Industry2] Solutions Architect  
                 ...  
                 
                 
                 ### c) Phase 2: Specialization (Later)  
                 *Requirements:*  
                 - Level 1 Skill Assessment (Free)  
                 - Level 1 Industry Assessment (Free)  
                 
                 
                 *Guided Industry AI Projects (Premium):*  
                 - [Industry1]: [Project1]  
                 - [Industry2]: [Project2]  
                 ….6 Projects  
                   🐾 Animal Habitat Conservation  
                   ☁ AI-Powered Weather Prediction  
                   ...  
                 
                 
                 *Personal Branding:* (must include minimum actionable suggestions, same level as other sections like 'Personality Assessment') 
                 - LinkedIn Optimization Guide  
                 - Portfolio Building Templates 


                 Rules:
                 Auto-generate ALL bracketed content ([Dominant Function], [Project1], etc.) based on:
                 Standard MBTI/personality frameworks
                 The 2 selected industries
                 The preferred role
                 Never add/remove sections - maintain this exact() structure 
                 Keep tone professional yet encouraging
                 Example Input Now:
                 Name: {Name}  
                 Personality Type: {PersonalityType}  
                 Selected Interests: {SelectedInterests[0]}, {SelectedInterests[1]}  
                 Preferred Role: {PreferredRole} 
                 Career Level: {CareerLevel} 
                 Key Features:
                 ✅ Auto-populates cognitive functions (INTP → "Introverted Thinking"). Also don’t use 4 Letter code or MBTI  but use Personality word for MBTI
                 ✅ Generates industry-specific TED Talks and projects
                 ✅ Maintains your exact formatting with emojis and sections
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

        extracted_data = extract_sections(raw)
      

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{Name}'s Personality Assessment</title>
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
        .note {{
            font-style: italic;
            color: #555;
        }}
    </style>
</head>
<body>
    <h1>{Name}'s Personality Assessment Report</h1>

    <section>
        <h2 class="section-title">🌟 How You Shine</h2>
        <ul>
            {''.join(f'<li>{item}</li>' for item in extracted_data['how_you_shine'])}
        </ul>
    </section>

    <section>
        <h2 class="section-title">🦸 Your Superpowers at Work</h2>
        <ul>
            {''.join(f'<li>{item}</li>' for item in extracted_data['your_superpowers_at_work'])}
        </ul>
    </section>

    <section>
        <h2 class="section-title">💼 Your Career Personality Type</h2>
        <ul>
            {''.join(f'<li>{item}</li>' for item in extracted_data['your_career_personality_type'])}
        </ul>
    </section>

    <section>
        <h2 class="section-title">🧠 Cognitive Functions</h2>
        <ul>
            {''.join(f'<li>{item}</li>' for item in extracted_data['cognitive_functions'])}
        </ul>
    </section>

    <section>
        <h2 class="section-title">🎯 Primary Role</h2>
        <ul>
            {''.join(f'<li>{item}</li>' for item in extracted_data['primary_role'])}
        </ul>
    </section>

    <section>
        <h2 class="section-title">🛠 Alternative Role</h2>
        <ul>
            {''.join(f'<li>{item}</li>' for item in extracted_data['alternative_role'])}
        </ul>
    </section>

    <section>
        <h2 class="section-title">🎤 Recommended TED Talks</h2>
        <ul>
            {''.join(f'<li>{item}</li>' for item in extracted_data['ted_talks'])}
        </ul>
    </section>

    <section>
        <h2 class="section-title">👥 Target Interviews</h2>
        <ul>
            {''.join(f'<li>{item}</li>' for item in extracted_data['interviews'])}
        </ul>
    </section>

    <section>
        <h2 class="section-title">🚀 Guided Projects</h2>
        <ul>
            {''.join(f'<li>{item}</li>' for item in extracted_data['guided_projects'])}
        </ul>
    </section>

    <section>
        <h2 class="section-title">📌 Personal Branding Tips</h2>
        <h3>LinkedIn</h3>
        <p>{extracted_data['personal_branding']['linkedin'].strip(': ')}</p>
        <h3>Portfolio</h3>
        <p>{extracted_data['personal_branding']['portfolio'].strip(': ')}</p>
    </section>
</body>
</html>
"""


        pdf_file_path = f"{Name}_Personality_Assessment.pdf"
        HTML(string=html_content).write_pdf(pdf_file_path)
        return pdf_file_path

    except Exception as error:
        raise error

    finally:
        pass


def extract_sections(response: str):
    def extract_list_items(text):
        lines = re.findall(r'-\s*(.+)', text)
        return [line.strip() for line in lines]
    sections = {}

    # Extract raw text
    raw_how_you_shine = re.search(
        r'### a\) Personality Assessment\s+1\. \*How You Shine Naturally:\*([\s\S]+?)\n\s+2\.', response).group(1).strip()
    raw_superpowers = re.search(
        r'2\. \*Your Superpowers at Work:\*([\s\S]+?)\n\s+3\.', response).group(1).strip()
    raw_career_personality = re.search(
        r'3\. \*Your Career Personality Type:\*.+?\n([\s\S]+?)\n\s+4\.', response).group(1).strip()
    raw_cognitive_functions = re.search(
        r'4\. \*Cognitive Functions:\*([\s\S]+?)\n\s+###', response).group(1).strip()

    # Parse each section into arrays
    sections['how_you_shine'] = extract_list_items(raw_how_you_shine)
    sections['your_superpowers_at_work'] = extract_list_items(raw_superpowers)
    sections['your_career_personality_type'] = extract_list_items(
        raw_career_personality)
    sections['cognitive_functions'] = extract_list_items(
        raw_cognitive_functions)

    # What you should do NEXT
    sections['primary_role'] = re.search(
        r'\*Primary Role:\* (.+?)\n- Best Fit For: (.+?)\n- Self-Guided Booklet: (.+)', response).groups()
    sections['alternative_role'] = re.search(
        r'\*Alternative Role:\* (.+?)\n- Consider If You Prefer: (.+?)\n- Self-Guided Booklet: (.+)', response).groups()

    # TED Talks (basic fallback list extraction)
    ted_talks_match = re.search(
        r'\*2\)\* 10 TED Talks \(on Selected Industries\):\*\*(.+?)\n\s+\*3\)\*', response, re.DOTALL)
    if ted_talks_match:
        ted_talks_raw = ted_talks_match.group(1).strip()
    ted_talks_lines = ted_talks_raw.split('\n')

    cleaned_talks = []
    for line in ted_talks_lines:
        line = line.strip()
        if not line:
            continue

        # Remove leading number and dot
        if '.' in line:
            line = line.split('.', 1)[1].strip()

        # Remove surrounding quotes and smart quotes
        line = line.strip('"“”')

        cleaned_talks.append(line)

    sections['ted_talks'] = cleaned_talks

    # Interviews
    interviews_match = re.search(
        r'\*3\)\* 10 Professional Interviews:\*\*(.+?)\n\s+### c\)', response, re.DOTALL)
    if interviews_match:
        interviews_raw = interviews_match.group(1).strip()
        sections['interviews'] = [line.strip(
            "0123456789. ") for line in interviews_raw.strip().split('\n') if line.strip()]

    # Specialization - Projects
    projects_match = re.search(
        r'\*Guided Industry AI Projects \(Premium\):\*([\s\S]+?)\n\s+\*Personal Branding:', response)
    if projects_match:
        projects_text = projects_match.group(1).strip()
        project_lines = [line.strip('- ').strip()
                         for line in projects_text.split('\n') if line.strip()]
        sections['guided_projects'] = project_lines

    # Branding
    branding_match = re.search(
        r'\*Personal Branding:\*.*?- LinkedIn Optimization Guide\s*(.+?)\s*- Portfolio Building Templates\s*(.+?)(?=\n[#*]|$)',
        response,
        re.DOTALL
    )

    if branding_match:
        linkedin = branding_match.group(1).strip()
    portfolio = branding_match.group(2).strip()

    sections['personal_branding'] = {
        'linkedin': linkedin,
        'portfolio': portfolio
    }

    return sections
