from crewai import Agent
from api.hr.tools.candidate_tools import add_candidate_details, update_candidate_status, get_candidate_details
from api.hr.tools.email_tools import send_email_tool
from api.hr.tools.offer_tools import generate_offer_letter
from api.hr.tools.human_tools import ask_hiring_manager

class RecruitmentAgents:
    def resume_analyst(self):
        return Agent(
            role='Resume Analyst',
            goal='Extract candidate details and match resumes against job descriptions.',
            backstory=(
                "You are an expert technical recruiter. "
                "First, you extract key details from a resume to maintain a database. "
                "Then, you objectively evaluate the candidate against the Job Description."
            ),
            verbose=True,
            allow_delegation=False,
            tools=[add_candidate_details, update_candidate_status]
        )

    def interview_scheduler(self):
        return Agent(
            role='Interview Scheduler',
            goal='Communicate accurately with candidates based on their recruitment status.',
            backstory=(
                "You are a detailed-oriented Interview Scheduler. "
                "You ensure candidates receive timely and professional updates. "
                "You ALWAYS verify the candidate's email from the database before sending communications. "
                "You ensure the email clearly states the specific role they have been shortlisted for, as defined in the Job Description."
            ),
            verbose=True,
            allow_delegation=False,
            tools=[get_candidate_details, send_email_tool]
        )

    def offer_manager(self):
        return Agent(
            role='Offer Manager',
            goal='Manage the final offer rollout process with human oversight.',
            backstory=(
                "You are the HR finter. You interact with the Hiring Manager to confirm the selection. "
                "If selected, you generate the offer letter and send it. "
                "If not, you ensure the candidate is informed. "
                "You craft professional and welcoming offer emails that highlight why the candidate is a great fit for the specific role mentioned in the Job Description."
            ),
            verbose=True,
            allow_delegation=False,
            tools=[ask_hiring_manager, generate_offer_letter, send_email_tool, get_candidate_details]
        )
