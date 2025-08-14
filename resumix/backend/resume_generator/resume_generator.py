import jinja2
import os

# This is a hack to import from doc_utils
import sys
import time

import subprocess

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from resumix.backend.resume_generator.doc_utils import escape_for_latex

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resume")

# os.chdir(BASE_DIR)

TEMPLATE_NAME = "Simple"

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


def generate_pdf(
    json_resume: dict,
    output_path: str,
    template_name: str = TEMPLATE_NAME,
    tex_filename: str = None,
    prelim_section_ordering=None,
) -> str:
    
    """
    渲染 LaTeX 并用 tectonic 编译 PDF，输出到 output_path（必须是 *.pdf）。
    - 使用唯一的 .tex 文件名，避免并发/历史文件干扰
    - 不修改全局 CWD；subprocess.run(..., cwd=BASE_DIR, env=ENV)
    - 编译后原子替换到 output_path
    """
    import time
    import subprocess

    tmpl = template_name or TEMPLATE_NAME
    section_order = prelim_section_ordering or []

    # 0) 规范化输出：确保以 .pdf 结尾
    output_path = os.path.abspath(output_path)
    if not output_path.lower().endswith(".pdf"):
        output_path = output_path + ".pdf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 1) 生成唯一的 .tex 文件名，避免相互覆盖
    if tex_filename:
        tex_file = tex_filename
    else:
        tex_file = f"{tmpl}-resume-{int(time.time()*1000)}.tex"

    tex_path = os.path.join(BASE_DIR, tex_file)

    # 2) 渲染 .tex
    latex_content = generate_latex(
        template_name=tmpl,
        json_resume=json_resume,
        prelim_section_ordering=section_order,
    )
    os.makedirs(BASE_DIR, exist_ok=True)
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_content)
    print(f"[INFO] LaTeX 写入: {tex_path}")

    # 3) 编译（在 BASE_DIR 下执行）
    if tmpl not in template_commands:
        raise RuntimeError(f"Unknown template_name: {tmpl}")
    command = template_commands[tmpl](tex_file=os.path.basename(tex_path))
    subprocess.run(command, check=True, cwd=BASE_DIR, env=ENV)
    print("[SUCCESS] tectonic 编译完成")

    # 4) 找到此次编译生成的 PDF（与 .tex 同名）
    compiled_pdf = os.path.join(
        BASE_DIR, os.path.splitext(os.path.basename(tex_path))[0] + ".pdf"
    )

    # 兜底：部分模板可能产出固定名
    if not os.path.exists(compiled_pdf) or os.path.getsize(compiled_pdf) == 0:
        fallback = os.path.join(BASE_DIR, "resume.pdf")
        if os.path.exists(fallback) and os.path.getsize(fallback) > 0:
            compiled_pdf = fallback
        else:
            listing = "\n".join(sorted(os.listdir(BASE_DIR)))
            raise RuntimeError(
                "PDF 未按预期生成。\n"
                f"尝试: {compiled_pdf}\n"
                f"工作目录: {BASE_DIR}\n目录内容:\n{listing}"
            )

    # 5) 原子替换到目标 output_path（避免拷贝旧文件）
    tmp_out = output_path + ".tmp"
    with open(compiled_pdf, "rb") as src, open(tmp_out, "wb") as dst:
        dst.write(src.read())
    os.replace(tmp_out, output_path)

    return output_path


if __name__ == "__main__":

    json_resume = json_resume = {
        "basics": {
            "name": "Zhang S",
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

    generate_pdf(
        json_resume=json_resume,
        template_name=TEMPLATE_NAME,
        output_path="resume.pdf",
    )

    # # 调用 Jinja2 渲染生成 LaTeX 内容
    # latex_content = generate_latex(
    #     template_name=TEMPLATE_NAME,
    #     json_resume=json_resume,
    #     prelim_section_ordering=[],  # 可自定义顺序
    # )

    # # 将 LaTeX 内容写入 resume.tex

    # with open(TEX_PATH, "w", encoding="utf-8") as f:
    #     f.write(latex_content)
    # print(f"[INFO] LaTeX 源码已写入: {TEX_PATH}")

    # # 编译为 PDF
    # try:
    #     print(f"[INFO] 开始使用 tectonic 编译 PDF... {TEMPLATE_NAME}")
    #     command = template_commands[TEMPLATE_NAME](tex_file=TEX_FILENAME)

    #     print(ENV)
    #     subprocess.run(command, check=True, env=ENV)
    #     print("[SUCCESS] PDF 编译完成，输出为 resume.pdf")
    # except subprocess.CalledProcessError as e:
    #     print("[ERROR] PDF 编译失败：")
    #     print(e)
