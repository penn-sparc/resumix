#!/usr/bin/env python3
"""
Script to create an example resume PDF for testing the Resumix application.
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors


def create_resume_pdf():
    # Create PDF document
    doc = SimpleDocTemplate("example_resume.pdf", pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=12,
        spaceBefore=12,
        textColor=colors.darkblue
    )
    
    subsection_style = ParagraphStyle(
        'SubSection',
        parent=styles['Heading3'],
        fontSize=16,
        spaceAfter=6,
        spaceBefore=6,
        textColor=colors.black
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 14
    normal_style.spaceAfter = 6
    
    # Title
    story.append(Paragraph("John Smith - Software Engineer", title_style))
    story.append(Spacer(1, 12))
    
    # Personal Information
    story.append(Paragraph("Personal Information", section_style))
    personal_info = """
    <b>Name:</b> John Smith<br/>
    <b>Phone:</b> +1 (555) 123-4567<br/>
    <b>Email:</b> john.smith@email.com<br/>
    <b>Location:</b> San Francisco, CA<br/>
    <b>LinkedIn:</b> linkedin.com/in/johnsmith<br/>
    <b>GitHub:</b> github.com/johnsmith
    """
    story.append(Paragraph(personal_info, normal_style))
    story.append(Spacer(1, 12))
    
    # Education
    story.append(Paragraph("Education Background", section_style))
    
    story.append(Paragraph("Master of Science in Computer Science", subsection_style))
    education1 = """
    Stanford University, Stanford, CA<br/>
    <i>September 2020 - June 2022</i><br/>
    • GPA: 3.8/4.0<br/>
    • Relevant Coursework: Machine Learning, Distributed Systems, Database Systems<br/>
    • Thesis: "Optimizing Neural Network Performance using Distributed Computing"
    """
    story.append(Paragraph(education1, normal_style))
    
    story.append(Paragraph("Bachelor of Science in Software Engineering", subsection_style))
    education2 = """
    University of California, Berkeley, CA<br/>
    <i>September 2016 - May 2020</i><br/>
    • GPA: 3.7/4.0<br/>
    • Magna Cum Laude<br/>
    • Relevant Coursework: Data Structures, Algorithms, Software Engineering, Computer Networks
    """
    story.append(Paragraph(education2, normal_style))
    story.append(Spacer(1, 12))
    
    # Work Experience
    story.append(Paragraph("Work Experience", section_style))
    
    story.append(Paragraph("Senior Software Engineer", subsection_style))
    work1 = """
    <b>Google Inc.</b> | Mountain View, CA<br/>
    <i>July 2022 - Present</i><br/>
    • Developed and maintained large-scale distributed systems serving 100M+ users daily<br/>
    • Led a team of 5 engineers in designing microservices architecture using Kubernetes and Docker<br/>
    • Improved system performance by 40% through optimization of database queries and caching strategies<br/>
    • Implemented CI/CD pipelines using Jenkins and reduced deployment time by 60%<br/>
    • Technologies: Python, Java, Kubernetes, Docker, PostgreSQL, Redis, Apache Kafka
    """
    story.append(Paragraph(work1, normal_style))
    
    story.append(Paragraph("Software Engineer Intern", subsection_style))
    work2 = """
    <b>Microsoft Corporation</b> | Seattle, WA<br/>
    <i>June 2021 - August 2021</i><br/>
    • Built machine learning models for natural language processing using PyTorch and TensorFlow<br/>
    • Developed REST APIs using Node.js and Express.js to serve ML models<br/>
    • Collaborated with cross-functional teams to integrate AI features into Microsoft Office products<br/>
    • Achieved 85% accuracy in sentiment analysis model for customer feedback processing<br/>
    • Technologies: Python, PyTorch, TensorFlow, Node.js, Azure, MongoDB
    """
    story.append(Paragraph(work2, normal_style))
    
    story.append(Paragraph("Full-Stack Developer Intern", subsection_style))
    work3 = """
    <b>Startup XYZ</b> | San Francisco, CA<br/>
    <i>June 2020 - August 2020</i><br/>
    • Designed and implemented user-friendly web applications using React.js and Redux<br/>
    • Built scalable backend services using Python Flask and PostgreSQL<br/>
    • Implemented real-time features using WebSocket technology<br/>
    • Increased user engagement by 25% through implementation of responsive design<br/>
    • Technologies: React.js, Redux, Python, Flask, PostgreSQL, WebSocket
    """
    story.append(Paragraph(work3, normal_style))
    story.append(Spacer(1, 12))
    
    # Project Experience
    story.append(Paragraph("Project Experience", section_style))
    
    story.append(Paragraph("E-Commerce Platform (Personal Project)", subsection_style))
    project1 = """
    <i>January 2023 - March 2023</i><br/>
    • Built a full-stack e-commerce platform using MERN stack (MongoDB, Express.js, React.js, Node.js)<br/>
    • Implemented secure payment processing using Stripe API<br/>
    • Designed responsive UI/UX with modern design principles<br/>
    • Deployed on AWS using EC2, S3, and RDS services<br/>
    • <b>GitHub:</b> github.com/johnsmith/ecommerce-platform<br/>
    • <b>Technologies:</b> React.js, Node.js, MongoDB, Express.js, Stripe API, AWS
    """
    story.append(Paragraph(project1, normal_style))
    
    story.append(Paragraph("Real-Time Chat Application", subsection_style))
    project2 = """
    <i>September 2022 - November 2022</i><br/>
    • Developed a real-time messaging application supporting group chats and file sharing<br/>
    • Implemented WebSocket connections for instant messaging<br/>
    • Built authentication system using JWT tokens<br/>
    • Deployed using Docker containers and Kubernetes orchestration<br/>
    • <b>Technologies:</b> Socket.io, Node.js, React.js, MongoDB, Docker, Kubernetes
    """
    story.append(Paragraph(project2, normal_style))
    
    story.append(Paragraph("Machine Learning Stock Predictor", subsection_style))
    project3 = """
    <i>March 2021 - May 2021</i><br/>
    • Created a machine learning model to predict stock prices using historical data<br/>
    • Implemented LSTM neural networks using TensorFlow and Keras<br/>
    • Achieved 78% accuracy in predicting next-day stock movements<br/>
    • Built web interface for visualization using D3.js and Chart.js<br/>
    • <b>Technologies:</b> Python, TensorFlow, Keras, Pandas, NumPy, D3.js
    """
    story.append(Paragraph(project3, normal_style))
    story.append(Spacer(1, 12))
    
    # Technical Skills
    story.append(Paragraph("Technical Skills", section_style))
    
    story.append(Paragraph("Programming Languages", subsection_style))
    skills1 = """
    • <b>Proficient:</b> Python, JavaScript, Java, TypeScript<br/>
    • <b>Familiar:</b> C++, Go, SQL, HTML/CSS
    """
    story.append(Paragraph(skills1, normal_style))
    
    story.append(Paragraph("Frameworks & Libraries", subsection_style))
    skills2 = """
    • <b>Frontend:</b> React.js, Vue.js, Angular, Redux, HTML5, CSS3, Bootstrap<br/>
    • <b>Backend:</b> Node.js, Express.js, Flask, Django, Spring Boot<br/>
    • <b>Machine Learning:</b> TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy
    """
    story.append(Paragraph(skills2, normal_style))
    
    story.append(Paragraph("Databases & Storage", subsection_style))
    skills3 = """
    • <b>Relational:</b> PostgreSQL, MySQL, SQLite<br/>
    • <b>NoSQL:</b> MongoDB, Redis, Elasticsearch<br/>
    • <b>Cloud Storage:</b> AWS S3, Google Cloud Storage
    """
    story.append(Paragraph(skills3, normal_style))
    
    story.append(Paragraph("DevOps & Cloud", subsection_style))
    skills4 = """
    • <b>Containerization:</b> Docker, Kubernetes<br/>
    • <b>CI/CD:</b> Jenkins, GitHub Actions, GitLab CI<br/>
    • <b>Cloud Platforms:</b> AWS (EC2, S3, RDS, Lambda), Google Cloud Platform, Azure<br/>
    • <b>Monitoring:</b> Prometheus, Grafana, ELK Stack
    """
    story.append(Paragraph(skills4, normal_style))
    
    story.append(Paragraph("Development Tools", subsection_style))
    skills5 = """
    • <b>Version Control:</b> Git, GitHub, GitLab<br/>
    • <b>IDEs:</b> VS Code, IntelliJ IDEA, PyCharm<br/>
    • <b>Project Management:</b> Jira, Confluence, Slack<br/>
    • <b>Testing:</b> Jest, Pytest, JUnit, Selenium
    """
    story.append(Paragraph(skills5, normal_style))
    story.append(Spacer(1, 12))
    
    # Certifications & Awards
    story.append(Paragraph("Certifications & Awards", section_style))
    certs = """
    • <b>AWS Certified Solutions Architect</b> (2023)<br/>
    • <b>Google Cloud Professional Data Engineer</b> (2022)<br/>
    • <b>Dean's List</b> - UC Berkeley (2018, 2019, 2020)<br/>
    • <b>Best Innovation Award</b> - University Hackathon 2019
    """
    story.append(Paragraph(certs, normal_style))
    story.append(Spacer(1, 12))
    
    # Languages
    story.append(Paragraph("Languages", section_style))
    languages = """
    • <b>English:</b> Native<br/>
    • <b>Spanish:</b> Conversational<br/>
    • <b>Mandarin:</b> Basic
    """
    story.append(Paragraph(languages, normal_style))
    
    # Build PDF
    doc.build(story)
    print("✅ Example resume PDF created successfully: example_resume.pdf")


if __name__ == "__main__":
    try:
        create_resume_pdf()
    except ImportError as e:
        print("❌ Missing required package. Please install reportlab:")
        print("pip install reportlab")
        print(f"Error: {e}")
    except Exception as e:
        print(f"❌ Error creating PDF: {e}") 