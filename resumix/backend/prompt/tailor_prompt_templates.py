from resumix.backend.prompt.prompt_schema import SCHEMA, EXAMPLE

# --- Tailor 专用的各 section 指令，全部严格 JSON 输出 ---
TAILOR_INSTRUCTION = {
    "personal_info": (
        "Instructions:\n"
        "- Tailor ONLY the Basics fields to the target role.\n"
        "- Keep information factual; DO NOT invent or hallucinate missing fields.\n"
        "- Normalize phone (E.164 if possible), ensure website is a valid URL.\n"
        "- If a field is unknown, return an empty string for that field.\n"
        "- Return ONLY valid JSON matching the schema above.\n"
        "- Do NOT include markdown code blocks, comments, or explanations.\n"
        "- Prefix the output with exactly: Final Answer:\n"
        "- Return in a single line."
    ),
    "education": (
        "Instructions:\n"
        "- Keep ONLY education items that are relevant to the target role; preserve factual details.\n"
        "- Use YYYY-MM for startDate/endDate when present; do not fabricate dates.\n"
        "- You may reorder items for relevance but MUST NOT change facts.\n"
        "- Return ONLY valid JSON matching the schema above.\n"
        "- Do NOT include markdown code blocks, comments, or explanations.\n"
        "- Prefix the output with exactly: Final Answer:\n"
        "- Return in a single line."
    ),
    "experience": (
        "Instructions:\n"
        "- Tailor ONLY work experience (exclude projects embedded elsewhere).\n"
        "- Rewrite highlights using STAR (Situation, Task, Action, Result) without naming STAR.\n"
        "- Prefer concise, active voice; quantify results when grounded by CV/JD.\n"
        "- Keep dates and titles factual; do NOT invent.\n"
        "- Return ONLY valid JSON matching the schema above.\n"
        "- Do NOT include markdown code blocks, comments, or explanations.\n"
        "- Prefix the output with exactly: Final Answer:\n"
        "- Return in a single line."
    ),
    "projects": (
        "Instructions:\n"
        "- Include ONLY projects relevant to the target role and present in the CV.\n"
        "- Adapt descriptions/keywords toward the role; do NOT invent technologies.\n"
        "- Keep URLs only if present and valid.\n"
        "- Return ONLY valid JSON matching the schema above.\n"
        "- Do NOT include markdown code blocks, comments, or explanations.\n"
        "- Prefix the output with exactly: Final Answer:\n"
        "- Return in a single line."
    ),
    "skills": (
        "Instructions:\n"
        "- Include up to the top 4 most relevant skills to the target role.\n"
        "- Prioritize alignment with work/education; do NOT invent skills not supported by CV.\n"
        "- Use concise keywords; deduplicate and group meaningfully.\n"
        "- Return ONLY valid JSON matching the schema above.\n"
        "- Do NOT include markdown code blocks, comments, or explanations.\n"
        "- Prefix the output with exactly: Final Answer:\n"
        "- Return in a single line."
    ),
    "awards": (
        "Instructions:\n"
        "- Include ONLY awards/certifications recognizably present in the CV.\n"
        "- Prefer items relevant to the target role; keep dates factual.\n"
        "- Return ONLY valid JSON matching the schema above.\n"
        "- Do NOT include markdown code blocks, comments, or explanations.\n"
        "- Prefix the output with exactly: Final Answer:\n"
        "- Return in a single line."
    ),
}


# --- Tailor Prompt 按 section 拆分，全部复用你已有的 SCHEMA / EXAMPLE ---
# 占位符：<CV_TEXT>（必填），<JOB_TITLE>（目标职位，可选），<JD_TEXT>（完整 JD，可选）
TAILOR_PROMPT_MAP = {
    "personal_info": f"""
You are going to TAILOR the Basics section of a resume to a target role.

CV:
<CV_TEXT>

Job Description (optional):
<JD_TEXT>

Now consider the following TypeScript Interface for the JSON schema:

{SCHEMA["basics"]}
{TAILOR_INSTRUCTION["personal_info"]}
{EXAMPLE["basics"]}
""",
    "education": f"""
You are going to TAILOR the Education section of a resume to a target role.

CV:
<CV_TEXT>

Target Role (optional):
<JOB_TITLE>

Job Description (optional):
<JD_TEXT>

Now consider the following TypeScript Interface for the JSON schema:

{SCHEMA["education"]}
{TAILOR_INSTRUCTION["education"]}
{EXAMPLE["education"]}
""",
    "experience": f"""
You are going to TAILOR the Work Experience section of a resume to a target role.

CV:
<CV_TEXT>

Target Role (optional):
<JOB_TITLE>

Job Description (optional):
<JD_TEXT>

Now consider the following TypeScript Interface for the JSON schema:

{SCHEMA["experience"]}
- Be specific rather than general; prefer active voice.
- Fix grammar and clarity; de-jargon when needed.
- Rewrite highlight bullets using STAR implicitly; quantify results when grounded by CV/JD.
{TAILOR_INSTRUCTION["experience"]}
{EXAMPLE["experience"]}
""",
    "projects": f"""
You are going to TAILOR the Projects section of a resume to a target role.

CV:
<CV_TEXT>

Target Role (optional):
<JOB_TITLE>

Job Description (optional):
<JD_TEXT>

Now consider the following TypeScript Interface for the JSON schema:

{SCHEMA["projects"]}
- Emphasize project outcomes, scale, and role-relevant technologies from the CV.
{TAILOR_INSTRUCTION["projects"]}
{EXAMPLE["projects"]}
""",
    "skills": f"""
You are going to TAILOR the Skills section of a resume to a target role.

CV:
<CV_TEXT>

Target Role (optional):
<JOB_TITLE>

Job Description (optional):
<JD_TEXT>

Now consider the following TypeScript Interface for the JSON schema:

{SCHEMA["skills"]}
- Choose the most role-relevant skills grounded by the CV; keep keywords concise and ATS-friendly.
{TAILOR_INSTRUCTION["skills"]}
{EXAMPLE["skills"]}
""",
    "awards": f"""
You are going to TAILOR the Awards/Certifications section of a resume to a target role.

CV:
<CV_TEXT>

Target Role (optional):
<JOB_TITLE>

Job Description (optional):
<JD_TEXT>

Now consider the following TypeScript Interface for the JSON schema:

{SCHEMA["awards"]}
- Prefer recent and role-relevant recognitions; keep factual details.\n
{TAILOR_INSTRUCTION["awards"]}
{EXAMPLE["awards"]}
""",
}
