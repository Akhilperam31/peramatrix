from crewai import Crew, Process
from api.hr.agents.recruitment_agents import RecruitmentAgents
from api.hr.tasks.recruitment_tasks import RecruitmentTasks

class RecruitmentCrew:
    def __init__(self, resume_content, job_description):
        self.resume_content = resume_content
        self.job_description = job_description

        agents = RecruitmentAgents()
        tasks = RecruitmentTasks()

        # Instantiate agents
        self.resume_analyst = agents.resume_analyst()
        self.interview_scheduler = agents.interview_scheduler()
        self.offer_manager = agents.offer_manager()

        # Instantiate tasks
        self.extraction = tasks.extraction_task(self.resume_analyst, self.resume_content)
        self.matching = tasks.matching_task(self.resume_analyst, self.resume_content, self.job_description)
        self.matching.context = [self.extraction]
        
        self.email = tasks.email_task(self.interview_scheduler, [self.matching])
        self.offer = tasks.offer_task(self.offer_manager, [self.matching, self.email])

    def screening_crew(self):
        return Crew(
            agents=[self.resume_analyst, self.interview_scheduler],
            tasks=[self.extraction, self.matching, self.email],
            verbose=True,
            process=Process.sequential
        )

    def offer_crew(self):
        return Crew(
            agents=[self.offer_manager],
            tasks=[self.offer],
            verbose=True,
            process=Process.sequential
        )
