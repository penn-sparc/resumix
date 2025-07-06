from pylatex import Document, Section, Command, Itemize, NewLine
from pylatex.utils import NoEscape
import os


def generate_pdf_resume(json_resume, output_path="resume"):
    doc = Document(documentclass="article")

    # 标题 & 基本信息
    name = json_resume["basics"]["name"]
    title = json_resume["basics"].get("label", "")
    email = json_resume["basics"].get("email", "")
    phone = json_resume["basics"].get("phone", "")
    website = json_resume["basics"].get("website", "")
    summary = json_resume["basics"].get("summary", "")

    doc.preamble.append(Command("title", f"{name} - {title}"))
    doc.preamble.append(Command("author", f"{email} \\ {phone} \\ {website}"))
    doc.preamble.append(Command("date", NoEscape(r"\today")))
    doc.append(NoEscape(r"\maketitle"))
    doc.append(summary)
    doc.append(NewLine())
    doc.append(NewLine())

    # 教育背景
    with doc.create(Section("教育背景")):
        for edu in json_resume.get("education", []):
            line = f"{edu['institution']}，{edu['area']}（{edu['startDate']} - {edu['endDate']}）"
            doc.append(line)
            doc.append(NewLine())

    # 工作经历
    with doc.create(Section("工作经历")):
        for work in json_resume.get("work", []):
            doc.append(
                f"{work['company']} - {work['position']} ({work['startDate']} ~ {work['endDate']})"
            )
            doc.append(NewLine())
            doc.append(work.get("summary", ""))
            doc.append(NewLine())

    # 技能
    with doc.create(Section("技能")):
        with doc.create(Itemize()) as itemize:
            for skill in json_resume.get("skills", []):
                itemize.add_item(f"{skill['name']}: {', '.join(skill['keywords'])}")

    # 项目经历
    with doc.create(Section("项目经历")):
        for proj in json_resume.get("projects", []):
            doc.append(f"{proj['name']}")
            doc.append(NewLine())
            doc.append(proj["description"])
            doc.append(NewLine())

    # 奖项
    with doc.create(Section("奖项")):
        for award in json_resume.get("awards", []):
            doc.append(
                f"{award['title']} - {award.get('awarder', '')} ({award['date']})"
            )
            doc.append(NewLine())
            doc.append(award.get("summary", ""))
            doc.append(NewLine())

    # 输出 PDF
    doc.generate_pdf(output_path, clean_tex=False)
    print(f"[SUCCESS] 简历已生成：{output_path}.pdf")


if __name__ == "__main__":
    json_resume = {
        "basics": {
            "name": "张三",
            "label": "后端工程师",
            "email": "zhangsan@example.com",
            "phone": "+86 123-4567-8901",
            "location": {"city": "北京", "region": "北京", "country": "中国"},
            "website": "https://zhangsan.dev",
            "summary": "热爱系统设计，具备丰富的后端与AI Agent开发经验",
        },
        "education": [
            {
                "institution": "清华大学",
                "area": "计算机科学与技术",
                "studyType": "本科",
                "startDate": "2018-09",
                "endDate": "2022-07",
                "gpa": "3.8/4.0",
            }
        ],
        "work": [
            {
                "company": "字节跳动",
                "position": "后端实习生",
                "startDate": "2022-07",
                "endDate": "2022-12",
                "summary": "负责视频推荐系统的服务性能优化与缓存策略设计",
            }
        ],
        "skills": [
            {"name": "编程语言", "keywords": ["Python", "Go", "C++"]},
            {"name": "数据库", "keywords": ["PostgreSQL", "MongoDB", "Redis"]},
        ],
        "projects": [
            {
                "name": "AI 简历优化助手",
                "description": "基于 RAG 与向量数据库构建的简历内容增强系统，提升匹配度与可读性",
                "keywords": ["RAG", "FastAPI", "FAISS"],
            }
        ],
        "awards": [
            {
                "title": "ACM ICPC 区域赛铜奖",
                "date": "2021-12",
                "awarder": "ACM Asia",
                "summary": "在区域赛中获得优异成绩",
            }
        ],
    }

    generate_pdf_resume(json_resume, output_path="resume")
