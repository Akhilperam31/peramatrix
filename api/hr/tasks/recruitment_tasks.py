from crewai import Task

class RecruitmentTasks:
    def extraction_task(self, agent, resume_content):
        return Task(
            description=(
                f"Read the resume content below:\n{resume_content}\n\n"
                "1. Extract the following details: Name, Email, Phone Number, Experience (Years), and Key Skills.\n"
                "2. Use the `AddCandidateDetails` tool to save these details to the database.\n"
                "Note: Ensure the Name is extracted accurately as it will be used for updating the status later."
            ),
            expected_output="Candidate details saved to database.",
            agent=agent
        )

    def matching_task(self, agent, resume_content, job_description):
        return Task(
            description=(
                "Compare the candidate's Resume against the Job Description (JD) to ensure a precise match.\n"
                f"**Job Description**:\n{job_description}\n\n"
                f"**Resume**:\n{resume_content}\n\n"
                "**Scoring Criteria**:\n"
                "1. **Skills (40%)**: Match technical skills mentioned in the JD. Look for exact matches and synonyms.\n"
                "2. **Experience (30%)**: Verify relevant industry experience and years of experience.\n"
                "3. **Education (20%)**: Check if the candidate matches the educational background instructions.\n"
                "4. **Culture/Soft Skills (10%)**: Assess project leadership, collaboration, and other soft skills.\n\n"
                "**Instructions**:\n"
                "1. Perform a detailed analysis based on the criteria above.\n"
                "2. Calculate the total score out of 100.\n"
                "3. Determine the status: 'Shortlisted' ONLY if the Weighted Score is > 80. Otherwise 'Not Shortlisted'.\n"
                "4. Provide a strictly evidence-based justification. Mention specifically what matched and what is missing.\n"
                "5. Use the `UpdateCandidateStatus` tool to update the database record for the candidate (using their Name extracted earlier)."
            ),
            expected_output="Report containing Candidate Name, Score, Status, and Justification (for next agent context).",
            agent=agent
        )

    def email_task(self, agent, context):
        return Task(
            description=(
                "Based on the output of the matching task:\n"
                "1. Identify the Candidate Name.\n"
                "2. Use `GetCandidateDetails` to retrieve the Email and confirmed Status from the database.\n"
                "3. Compose a professional email:\n"
                "   - If Status is 'Shortlisted': Subject: 'Interview Invitation - [Job Title]'. Body: Congratulate them on being shortlisted for the [Job Title] role. Ensure the role name is exactly as mentioned in the Job Description. Propose a time for the interview.\n"
                "   - If Status is 'Not Shortlisted': Subject: 'Update on your Application - [Job Title]'. Body: Thank you for applying to the [Job Title] position. Be empathetic. Mention that while their profile is impressive, we are proceeding with other candidates who have a closer match for the specific requirements of this role.\n"
                "4. Use `SendEmailTool` to send the email.\n"
                "IMPORTANT: You MUST explicitly output 'STATUS: Shortlisted' or 'STATUS: Not Shortlisted' so the next step knows whether to proceed."
            ),
            expected_output="STATUS: [Status]. Email sent to [Email].",
            agent=agent,
            context=context
        )

    def offer_task(self, agent, context):
        return Task(
            description=(
                "**Offer Process**\n"
                "1. Find the Candidate Name in the provided RESUME CONTENT below. EXTRACT IT.\n"
                "2. The Decision is: {decision}.\n"
                "3. The CTC is: {ctc}.\n"
                "4. Use `GetCandidateDetails` tool with the EXTRACTED Name to get the correct Email from the database.\n"
                "5. IF Decision is 'Selected':\n"
                "   - Use `GenerateOfferLetter` to create the PDF for the Candidate with {ctc}.\n"
                "   - Use `SendEmailTool` to send an email with Subject: 'Offer Letter - [Job Title]' and attach the PDF.\n"
                "   - Email Body: Warmly congratulate them on the offer for the [Job Title] role. Mention that their skills in [Key Skills] made them a standout candidate. Express excitement about them joining the team. Provide clear instructions to sign and return the attached offer letter.\n"
                "6. IF Decision is 'Not Selected' or 'Rejected':\n"
                "   - Use `SendEmailTool` to send a helpful rejection email. Encourage them to apply for future roles."
            ),
            expected_output="Final decision executed (Offer sent or Rejection sent).",
            agent=agent,
            context=context
        )
