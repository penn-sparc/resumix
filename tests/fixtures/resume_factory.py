import factory
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()

class ResumeFactory(factory.Factory):
    class Meta:
        model = dict
    
    name = factory.LazyFunction(fake.name)
    email = factory.LazyFunction(fake.email)
    phone = factory.LazyFunction(fake.phone_number)
    
    @factory.lazy_attribute
    def personal_info_text(self):
        return f"""
        {self.name}
        Software Engineer
        {self.email}
        {self.phone}
        LinkedIn: linkedin.com/in/{self.name.lower().replace(' ', '')}
        San Francisco, CA
        """
    
    @factory.lazy_attribute
    def experience_text(self):
        companies = [fake.company() for _ in range(random.randint(2, 4))]
        jobs = [fake.job() for _ in range(len(companies))]
        
        experiences = []
        current_date = datetime.now()
        
        for i, (company, job) in enumerate(zip(companies, jobs)):
            start_date = current_date - timedelta(days=random.randint(365*i, 365*(i+3)))
            end_date = current_date - timedelta(days=random.randint(0, 365*i)) if i > 0 else "Present"
            
            experience = f"""
            {job} | {company} | {start_date.strftime('%b %Y')} - {end_date if isinstance(end_date, str) else end_date.strftime('%b %Y')}
            • {fake.sentence()}
            • {fake.sentence()}
            • {fake.sentence()}
            """
            experiences.append(experience)
        
        return "\n".join(experiences)
    
    @factory.lazy_attribute  
    def education_text(self):
        degrees = ['Bachelor', 'Master', 'PhD']
        fields = ['Computer Science', 'Software Engineering', 'Information Technology', 'Computer Engineering']
        schools = ['MIT', 'Stanford', 'Harvard', 'UC Berkeley', 'Carnegie Mellon', 'Georgia Tech']
        
        education_entries = []
        for i in range(random.randint(1, 2)):
            degree = random.choice(degrees)
            field = random.choice(fields)
            school = random.choice(schools)
            year = fake.year()
            gpa = round(random.uniform(3.0, 4.0), 2)
            
            education = f"""
            {degree} of Science in {field} | {school} | {year}
            GPA: {gpa}/4.0
            """
            education_entries.append(education)
        
        return "\n".join(education_entries)
    
    @factory.lazy_attribute
    def skills_text(self):
        programming_languages = random.sample([
            'Python', 'JavaScript', 'Java', 'C++', 'Go', 'Rust', 'TypeScript', 'C#'
        ], k=random.randint(3, 6))
        
        frameworks = random.sample([
            'React', 'Angular', 'Vue.js', 'Django', 'Flask', 'Express.js', 'Spring Boot'
        ], k=random.randint(2, 4))
        
        databases = random.sample([
            'PostgreSQL', 'MongoDB', 'MySQL', 'Redis', 'Elasticsearch'
        ], k=random.randint(2, 3))
        
        cloud = random.sample([
            'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes'
        ], k=random.randint(2, 3))
        
        return f"""
        Programming Languages: {', '.join(programming_languages)}
        Frameworks: {', '.join(frameworks)}
        Databases: {', '.join(databases)}
        Cloud & DevOps: {', '.join(cloud)}
        """
    
    @factory.lazy_attribute
    def projects_text(self):
        projects = []
        for i in range(random.randint(2, 4)):
            project_name = f"{fake.word().title()} {random.choice(['App', 'Platform', 'System', 'Tool'])}"
            technologies = random.sample([
                'Python', 'React', 'Node.js', 'PostgreSQL', 'AWS', 'Docker'
            ], k=3)
            
            project = f"""
            {project_name}
            • {fake.sentence()}
            • {fake.sentence()}
            • Technologies: {', '.join(technologies)}
            """
            projects.append(project)
        
        return "\n".join(projects)
    
    @factory.lazy_attribute
    def full_resume_text(self):
        return f"""
        {self.personal_info_text}
        
        EXPERIENCE
        {self.experience_text}
        
        EDUCATION
        {self.education_text}
        
        SKILLS
        {self.skills_text}
        
        PROJECTS
        {self.projects_text}
        """

class JobDescriptionFactory(factory.Factory):
    class Meta:
        model = dict
    
    title = factory.LazyFunction(lambda: fake.job())
    company = factory.LazyFunction(fake.company)
    location = factory.LazyFunction(fake.city)
    
    @factory.lazy_attribute
    def requirements(self):
        base_requirements = [
            f"{random.randint(3, 7)}+ years of experience in software development",
            "Bachelor's degree in Computer Science or related field",
            "Strong problem-solving and analytical skills",
            "Excellent communication and teamwork abilities"
        ]
        
        technical_requirements = random.sample([
            "Proficiency in Python and/or JavaScript",
            "Experience with React or similar frontend frameworks",
            "Knowledge of database systems (SQL/NoSQL)",
            "Familiarity with cloud platforms (AWS, Azure, GCP)",
            "Experience with version control systems (Git)",
            "Understanding of software testing methodologies"
        ], k=random.randint(3, 5))
        
        return base_requirements + technical_requirements
    
    @factory.lazy_attribute
    def responsibilities(self):
        return random.sample([
            "Design and develop scalable software applications",
            "Collaborate with cross-functional teams",
            "Write clean, maintainable, and efficient code",
            "Participate in code reviews and technical discussions",
            "Troubleshoot and debug applications",
            "Mentor junior developers",
            "Stay up-to-date with emerging technologies",
            "Contribute to technical documentation"
        ], k=random.randint(5, 7))
    
    @factory.lazy_attribute
    def nice_to_have(self):
        return random.sample([
            "Experience with microservices architecture",
            "Knowledge of containerization (Docker, Kubernetes)",
            "Familiarity with CI/CD pipelines",
            "Experience with machine learning frameworks",
            "Contributions to open source projects",
            "Advanced degree in Computer Science",
            "Relevant certifications"
        ], k=random.randint(2, 4))
    
    @factory.lazy_attribute
    def full_description(self):
        return f"""
        {self.title} - {self.company}
        Location: {self.location}
        
        We are looking for a talented {self.title} to join our growing team.
        
        Requirements:
        {chr(10).join([f'• {req}' for req in self.requirements])}
        
        Responsibilities:
        {chr(10).join([f'• {resp}' for resp in self.responsibilities])}
        
        Nice to have:
        {chr(10).join([f'• {nice}' for nice in self.nice_to_have])}
        """