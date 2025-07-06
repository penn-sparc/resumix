SYSTEM_PROMPT = "You are a smart assistant to career advisors at the Harvard Extension School. You will reply with JSON only."

TAILORING_PROMPT = """
Consider the following CV:
<CV_TEXT>

Your task is to rewrite the given CV. Follow these guidelines:
- Be truthful and objective to the experience listed in the CV
- Be specific rather than general
- Rewrite job highlight items using STAR methodology (but do not mention STAR explicitly)
- Fix spelling and grammar errors
- Write to express not impress
- Articulate and don't be flowery
- Prefer active voice over passive voice
- Do not include a summary about the candidate

Improved CV:
"""
BASICS_PROMPT = """
You are going to write a JSON resume section for an applicant applying for job posts.

Consider the following CV:
<CV_TEXT>

Now consider the following TypeScript Interface for the JSON schema:

interface Basics {
    name: string;
    email: string;
    phone: string;
    website: string;
    address: string;
}

Instructions:
- Return only valid JSON matching the schema above.
- Do NOT include markdown code blocks, comments, or explanations.
- Prefix the output with exactly: Final Answer:
- Return in a single line.

Example output:
Final Answer: {"name": "John Doe", "email": "john@example.com", "phone": "1234567890", "website": "https://example.com", "address": "123 Main St"}
"""

EDUCATION_PROMPT = """
You are going to write a JSON resume section for an applicant applying for job posts.

Consider the following CV:
<CV_TEXT>

Now consider the following TypeScript Interface for the JSON schema:

interface EducationItem {
    institution: string;
    area: string;
    additionalAreas: string[];
    studyType: string;
    startDate: string;
    endDate: string;
    score: string;
    location: string;
}

interface Education {
    education: EducationItem[];
}

Instructions:
- Return only valid JSON matching the schema above.
- Do NOT include markdown code blocks, comments, or explanations.
- Prefix the output with exactly: Final Answer:
- Return in a single line.

Example output:
Final Answer: {"education":[{"institution":"Harvard University","area":"Computer Science","additionalAreas":[],"studyType":"Bachelor","startDate":"2015-09","endDate":"2019-06","score":"3.9/4.0","location":"Cambridge, MA"}]}
"""

WORK_PROMPT = """
You are going to write a JSON resume section for an applicant applying for job posts.

Consider the following CV:
<CV_TEXT>

Now consider the following TypeScript Interface for the JSON schema:

interface WorkItem {
    company: string;
    position: string;
    startDate: string;
    endDate: string;
    location: string;
    highlights: string[];
}

interface Work {
    work: WorkItem[];
}

Instructions:
- Write only the work experience section (exclude projects).
- Use STAR methodology in highlights (Situation, Task, Action, Result).
- Follow Harvard Extension School Resume standards.
- Return only valid JSON matching the schema above.
- Do NOT include markdown code blocks, comments, or explanations.
- Prefix the output with exactly: Final Answer:
- Return in a single line.

Example output:
Final Answer: {"work":[{"company":"Google","position":"Software Engineer","startDate":"2020-01","endDate":"2022-12","location":"Mountain View, CA","highlights":["Led redesign of search interface, improving user engagement by 15%.","Implemented A/B testing pipeline reducing experimentation time by 30%."]}]}
"""

PROJECTS_PROMPT = """
You are going to write a JSON resume section for an applicant applying for job posts.

Consider the following CV:
<CV_TEXT>

Now consider the following TypeScript Interface for the JSON schema:

interface ProjectItem {
    name: string;
    description: string;
    keywords: string[];
    url: string;
}

interface Projects {
    projects: ProjectItem[];
}

Instructions:
- Include only projects present in the CV.
- Return only valid JSON matching the schema above.
- Do NOT include markdown code blocks, comments, or explanations.
- Prefix the output with exactly: Final Answer:
- Return in a single line.

Example output:
Final Answer: {"projects":[{"name":"Resume AI","description":"Built a resume parser using NLP and LLM.","keywords":["NLP","LLM","Python"],"url":"https://github.com/example/resume-ai"}]}
"""

SKILLS_PROMPT = """
You are going to write a JSON resume section for an applicant applying for job posts.

Consider the following CV:
<CV_TEXT>

type HardSkills = "Programming Languages" | "Tools" | "Frameworks" | "Computer Proficiency";
type SoftSkills = "Team Work" | "Communication" | "Leadership" | "Problem Solving" | "Creativity";
type OtherSkills = string;

Now consider the following TypeScript Interface for the JSON schema:

interface SkillItem {
    name: HardSkills | SoftSkills | OtherSkills;
    keywords: string[];
}

interface Skills {
    skills: SkillItem[];
}

Instructions:
- Include up to the top 4 relevant skills present in the CV.
- Prioritize those related to work and education background.
- Return only valid JSON matching the schema above.
- Do NOT include markdown code blocks, comments, or explanations.
- Prefix the output with exactly: Final Answer:
- Return in a single line.

Example output:
Final Answer: {"skills":[{"name":"Programming Languages","keywords":["Python","C++"]},{"name":"Frameworks","keywords":["React","PyTorch"]}]}
"""

PROMPT_MAP = {
    "personal_info": BASICS_PROMPT,
    "education": EDUCATION_PROMPT,
    "experience": WORK_PROMPT,
    "projects": PROJECTS_PROMPT,
    "skills": SKILLS_PROMPT,
    "tailor": TAILORING_PROMPT,
}

PROJECTS_SCORE_PROMPT = """
You are a professional HR analyst.
Please evaluate the following **resume section** based on the provided **job description** and rate it from 0 to 10 across six key criteria.

## Job Description

**Basic Requirements**:
<JD_BASIC_TEXT>

**Preferred Requirements**:
<JD_PREFERRED_TEXT>

## Resume Section:
<CV_TEXT>

## Evaluation Instructions:

Score the section on a scale from 0 to 10 for each dimension below.
Give an integer score and concise explanation.
If a dimension is not applicable, assign 0 and explain why.

### Evaluation Dimensions:
- **Completeness**: Does the section provide complete and sufficient information?
- **Clarity**: Is the writing clear, organized, and easy to follow?
- **Relevance**: Does the content align with the basic and preferred requirements?
- **Professional Language**: Does the candidate use appropriate technical and formal language?
- **Achievement-Oriented**: Are accomplishments and results emphasized?
- **Quantitative Support**: Are there any numbers, data, or measurable indicators?

At the end, give a concise **comment** summarizing strengths and improvement suggestions.

## Output JSON Format

You must return **only** valid JSON in the following format:

interface ScoreResult {
  "Completeness": int;
  "Clarity": int;
  "Relevance": int;
  "ProfessionalLanguage": int;
  "AchievementOriented": int;
  "QuantitativeSupport": int;
  "Comment": str;
}
"""

SCORE_PROMPT_MAP = {
    "personal_info": PROJECTS_SCORE_PROMPT,
    "education": PROJECTS_SCORE_PROMPT,
    "experience": PROJECTS_SCORE_PROMPT,
    "projects": PROJECTS_SCORE_PROMPT,
    "skills": PROJECTS_SCORE_PROMPT,
}


TECHSTACK_TAILORING_PROMPT = """
You are a professional resume assistant specializing in tailoring CVs to technical job positions.

## CV Content:
{CV_TEXT}

## Target Position:
{JOB_POSITION}

## User's Technical Stack:
{TECH_STACK}

## Instructions:
Your task is to optimize the given CV content for the specified job position and highlight relevant technical experience. Follow these guidelines:

- Emphasize the use of technologies mentioned in {JOB_POSITION}, either explicitly or through appropriate context
- Highlight any work that matches the responsibilities or domain implied by {JOB_POSITION}
- Rewrite experience items using clear, professional language and quantifiable results where possible
- Use active voice and concise phrasing; avoid repetition and vague descriptions
- If a technology in {TECH_STACK} is not mentioned but can be reasonably inferred based on context, include it
- If relevant experience is missing, suggest a placeholder line the candidate could consider adding


## Output:
Return the optimized CV section, with commentary and explanation.
"""
