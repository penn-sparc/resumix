SCHEMA = SCHEMA = {
    "basics": r"""
interface Basics {
  name: string;
  email: string;
  phone: string;
  website: string;
  address: string;
}
""",
    "education": r"""
interface EducationItem {
  institution: string;
  area: string;
  additionalAreas: string[];
  studyType: string;
  startDate: string; // YYYY-MM
  endDate: string;   // YYYY-MM | "Present"
  score: string;
  location: string;
}

interface Education {
  education: EducationItem[];
}
""",
    "experience": r"""
interface WorkItem {
  company: string;
  position: string;
  startDate: string; // YYYY-MM
  endDate: string;   // YYYY-MM | "Present"
  location: string;
  highlights: string[]; // Use STAR style bullets
}

interface Work {
  work: WorkItem[];
}
""",
    "projects": r"""
interface ProjectItem {
  name: string;
  description: string;
  keywords: string[];
  url: string;
}

interface Projects {
  projects: ProjectItem[];
}
""",
    "skills": r"""
type HardSkills = "Programming Languages" | "Tools" | "Frameworks" | "Computer Proficiency";
type SoftSkills = "Team Work" | "Communication" | "Leadership" | "Problem Solving" | "Creativity";
type OtherSkills = string;

interface SkillItem {
  name: HardSkills | SoftSkills | OtherSkills;
  keywords: string[];
}

interface Skills {
  skills: SkillItem[];
}
""",
    "awards": r"""
interface AwardItem {
  title: string;
  date: string;     // YYYY or YYYY-MM
  awarder: string;
  summary: string;
}

interface Awards {
  awards: AwardItem[];
}
""",
}

EXAMPLE = {
    "basics": 'Final Answer: {"name":"John Doe","email":"john@example.com","phone":"1234567890","website":"https://example.com","address":"123 Main St"}',
    "education": 'Final Answer: {"education":[{"institution":"Harvard University","area":"Computer Science","additionalAreas":[],"studyType":"Bachelor","startDate":"2015-09","endDate":"2019-06","score":"3.9/4.0","location":"Cambridge, MA"}]}',
    "experience": 'Final Answer: {"work":[{"company":"Google","position":"Software Engineer","startDate":"2020-01","endDate":"2022-12","location":"Mountain View, CA","highlights":["Faced X latency issue in service S; owned redesign; implemented async batching; reduced P95 latency by 30%.","Owned A/B infra migration; automated experiment rollout; cut setup time by 40%."]}]}',
    "projects": 'Final Answer: {"projects":[{"name":"Resume AI","description":"Built a resume parser using NLP and LLM.","keywords":["NLP","LLM","Python"],"url":"https://github.com/example/resume-ai"}]}',
    "skills": 'Final Answer: {"skills":[{"name":"Programming Languages","keywords":["Python","C++"]},{"name":"Frameworks","keywords":["React","PyTorch"]}]}',
    "awards": 'Final Answer: {"awards":[{"title":"AWS Certified Solutions Architect","date":"2023","awarder":"Amazon Web Services","summary":"Professional cloud architecture certification"}]}',
}


INSTRUCTION = {
    # ===== Basics =====
    "basics": (
        "Instructions:\n"
        "- Return only valid JSON matching the schema above.\n"
        "- Do NOT include markdown code blocks, comments, or explanations.\n"
        "- Prefix the output with exactly: Final Answer:\n"
        "- Return in a single line."
    ),
    # ===== Education =====
    "education": (
        "Instructions:\n"
        "- Return only valid JSON matching the schema above.\n"
        "- Do NOT include markdown code blocks, comments, or explanations.\n"
        "- Prefix the output with exactly: Final Answer:\n"
        "- Return in a single line."
    ),
    # ===== Work / Experience =====
    "experience": (
        "Instructions:\n"
        "- Write only the work experience section (exclude projects).\n"
        "- Use STAR methodology in highlights (Situation, Task, Action, Result).\n"
        "- Follow Harvard Extension School Resume standards.\n"
        "- Return only valid JSON matching the schema above.\n"
        "- Do NOT include markdown code blocks, comments, or explanations.\n"
        "- Prefix the output with exactly: Final Answer:\n"
        "- Return in a single line."
    ),
    # ===== Projects =====
    "projects": (
        "Instructions:\n"
        "- Include only projects present in the CV.\n"
        "- Return only valid JSON matching the schema above.\n"
        "- Do NOT include markdown code blocks, comments, or explanations.\n"
        "- Prefix the output with exactly: Final Answer:\n"
        "- Return in a single line."
    ),
    # ===== Skills =====
    "skills": (
        "Instructions:\n"
        "- Include up to the top 4 relevant skills present in the CV.\n"
        "- Prioritize those related to work and education background.\n"
        "- Return only valid JSON matching the schema above.\n"
        "- Do NOT include markdown code blocks, comments, or explanations.\n"
        "- Prefix the output with exactly: Final Answer:\n"
        "- Return in a single line."
    ),
    # ===== Awards =====
    "awards": (
        "Instructions:\n"
        "- Include only awards, certifications, and recognitions present in the CV.\n"
        "- Return only valid JSON matching the schema above.\n"
        "- Do NOT include markdown code blocks, comments, or explanations.\n"
        "- Prefix the output with exactly: Final Answer:\n"
        "- Return in a single line."
    ),
}
