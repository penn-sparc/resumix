import jinja2
import os

# This is a hack to import from doc_utils
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from resumix.backend.resume_generator.doc_utils import escape_for_latex

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resume")

os.chdir(BASE_DIR)

TEMPLATE_NAME = "Plush"

ENV = os.environ.copy()
ENV["TECTONIC_CACHE"] = os.path.join(os.path.dirname(__file__), "tectonic_cache")


# TEX_FILENAME = TEMPLATE_NAME + "-resume-" + time.strftime("%Y-%m-%d-%H-%-M-%S") + ".tex"
TEX_FILENAME = TEMPLATE_NAME + "-resume.tex"
TEX_PATH = os.path.join(BASE_DIR, TEX_FILENAME)

template_commands = {
    name: lambda tex_file: [
        "tectonic",
        tex_file,
        "-Z",
        "continue-on-errors",
        "--untrusted",
        # "--only-cached",
        "--outdir",
        ".",
    ]
    for name in ["Simple", "Awesome", "BGJC", "Deedy", "Modern", "Plush", "Alta"]
}

# template_commands = {
#     "Simple": [
#         "tectonic",
#         "-X",
#         "compile",
#         "-Z",
#         "continue-on-errors",
#         "--untrusted",
#         # "--only-cached",
#         "--outdir",
#         ".",
#         TEX_FILENAME,
#     ],
#     "Awesome": [
#         "tectonic",
#         "-X",
#         "compile",
#         "-Z",
#         "continue-on-errors",
#         "--untrusted",
#         # "--only-cached",
#         "--outdir",
#         ".",
#         TEX_FILENAME,
#     ],
#     "BGJC": [
#         "tectonic",
#         "-X",
#         "compile",
#         "-Z",
#         "continue-on-errors",
#         "--untrusted",
#         # "--only-cached",
#         "--outdir",
#         ".",
#         TEX_FILENAME,
#     ],
#     "Deedy": [
#         "tectonic",
#         "-X",
#         "compile",
#         "-Z",
#         "continue-on-errors",
#         "--untrusted",
#         # "--only-cached",
#         "--outdir",
#         ".",
#         TEX_FILENAME,
#     ],
#     "Modern": [
#         "tectonic",
#         "-X",
#         "compile",
#         "-Z",
#         "continue-on-errors",
#         "--untrusted",
#         # "--only-cached",
#         "--outdir",
#         ".",
#         TEX_FILENAME,
#     ],
#     "Plush": [
#         "tectonic",
#         "-X",
#         "compile",
#         "-Z",
#         "continue-on-errors",
#         "--untrusted",
#         # "--only-cached",
#         "--outdir",
#         ".",
#         TEX_FILENAME,
#     ],
#     "Alta": [
#         "tectonic",
#         "-X",
#         "compile",
#         "-Z",
#         "continue-on-errors",
#         "--untrusted",
#         # "--only-cached",
#         "--outdir",
#         ".",
#         TEX_FILENAME,
#     ],
# }


def generate_latex(template_name, json_resume, prelim_section_ordering):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    latex_jinja_env = jinja2.Environment(
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string=r"\#{",
        comment_end_string="}",
        line_statement_prefix="%-",
        line_comment_prefix="%#",
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(dir_path),
    )

    escaped_json_resume = escape_for_latex(json_resume)

    return use_template(
        template_name, latex_jinja_env, escaped_json_resume, prelim_section_ordering
    )


def use_template(template_name, jinja_env, json_resume, prelim_section_ordering):
    PREFIX = f"{template_name}"
    EXTENSION = "tex.jinja"

    resume_template = jinja_env.get_template(f"{PREFIX}/resume.{EXTENSION}")
    basics_template = jinja_env.get_template(f"{PREFIX}/basics.{EXTENSION}")
    education_template = jinja_env.get_template(f"{PREFIX}/education.{EXTENSION}")
    work_template = jinja_env.get_template(f"{PREFIX}/work.{EXTENSION}")
    skills_template = jinja_env.get_template(f"{PREFIX}/skills.{EXTENSION}")
    projects_template = jinja_env.get_template(f"{PREFIX}/projects.{EXTENSION}")
    awards_template = jinja_env.get_template(f"{PREFIX}/awards.{EXTENSION}")

    sections = {}
    section_ordering = get_final_section_ordering(prelim_section_ordering)

    if "basics" in json_resume:
        firstName = json_resume["basics"]["name"].split(" ")[0]
        lastName = " ".join(json_resume["basics"]["name"].split(" ")[1:])
        sections["basics"] = basics_template.render(
            firstName=firstName, lastName=lastName, **json_resume["basics"]
        )
    if "education" in json_resume and len(json_resume["education"]) > 0:
        sections["education"] = education_template.render(
            schools=json_resume["education"], heading="Education"
        )
    if "work" in json_resume and len(json_resume["work"]) > 0:
        sections["work"] = work_template.render(
            works=json_resume["work"], heading="Work Experience"
        )

    if "skills" in json_resume and len(json_resume["skills"]) > 0:
        sections["skills"] = skills_template.render(
            skills=json_resume["skills"], heading="Skills"
        )
    if "projects" in json_resume and len(json_resume["projects"]) > 0:
        sections["projects"] = projects_template.render(
            projects=json_resume["projects"], heading="Projects"
        )

    if "awards" in json_resume and len(json_resume["awards"]) > 0:
        sections["awards"] = awards_template.render(
            awards=json_resume["awards"], heading="Awards"
        )

    resume = resume_template.render(
        sections=sections, section_ordering=section_ordering
    )
    return resume


def get_final_section_ordering(section_ordering):
    final_ordering = ["basics"]
    additional_ordering = section_ordering + [
        "education",
        "work",
        "skills",
        "projects",
        "awards",
    ]
    for section in additional_ordering:
        if section not in final_ordering:
            final_ordering.append(section)

    return final_ordering


if __name__ == "__main__":
    import subprocess

    json_resume = json_resume = {
        "basics": {
            "name": "Zhang San",
            "address": "123 Tsinghua Road, Beijing, China",
            "email": "zhangsan@example.com",
            "phone": "+86 123-4567-8901",
            "website": "https://zhangsan.dev",
        },
        "education": [
            {
                "institution": "Tsinghua University",
                "location": "Beijing, China",
                "studyType": "Bachelor",
                "area": "Computer Science and Technology",
                "score": "3.8/4.0",
                "startDate": "2018-09",
                "endDate": "2022-07",
            }
        ],
        "work": [
            {
                "company": "ByteDance",
                "position": "Backend Intern",
                "location": "Beijing, China",
                "startDate": "2022-07",
                "endDate": "2022-12",
                "highlights": [
                    "Optimized microservice latency by 35% via Redis-based caching.",
                    "Designed an asynchronous pipeline for high-QPS video recommendation backend.",
                    "Collaborated with front-end team to reduce average user response time by 20%.",
                ],
            }
        ],
        "projects": [
            {
                "name": "AI Resume Optimization Assistant",
                "description": "A system leveraging RAG and vector DBs to rewrite and optimize resumes.",
                "keywords": ["RAG", "FastAPI", "FAISS"],
                "url": "https://github.com/zhangsan/ai-resume",
            }
        ],
        "awards": [
            {
                "title": "ACM ICPC Regional Bronze Medal",
                "date": "2021-12",
                "awarder": "ACM Asia",
                "summary": "Achieved outstanding performance in algorithmic regional competition.",
            }
        ],
        "skills": [
            {"name": "Programming Languages", "keywords": ["Python", "Go", "C++"]},
            {"name": "Databases", "keywords": ["PostgreSQL", "MongoDB", "Redis"]},
            {"name": "Tools", "keywords": ["Docker", "Git", "Linux"]},
            {"name": "Cloud", "keywords": ["GCP", "Kubernetes", "Terraform"]},
        ],
    }

    # 调用 Jinja2 渲染生成 LaTeX 内容
    latex_content = generate_latex(
        template_name=TEMPLATE_NAME,
        json_resume=json_resume,
        prelim_section_ordering=[],  # 可自定义顺序
    )

    # 将 LaTeX 内容写入 resume.tex

    with open(TEX_PATH, "w", encoding="utf-8") as f:
        f.write(latex_content)
    print(f"[INFO] LaTeX 源码已写入: {TEX_PATH}")

    # 编译为 PDF
    try:
        print(f"[INFO] 开始使用 tectonic 编译 PDF... {TEMPLATE_NAME}")
        command = template_commands[TEMPLATE_NAME](tex_file=TEX_FILENAME)

        print(ENV)
        subprocess.run(command, check=True, env=ENV)
        print("[SUCCESS] PDF 编译完成，输出为 resume.pdf")
    except subprocess.CalledProcessError as e:
        print("[ERROR] PDF 编译失败：")
        print(e)
