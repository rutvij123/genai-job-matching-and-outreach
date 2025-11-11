from langchain_core.prompts import PromptTemplate

EMAIL_TEMPLATE = PromptTemplate.from_template(
    """
    ### Job role:
    {job_role_name}
    ### Job description:
    {job_role_desc}

    ### INSTRUCTION:
    Write a concise cold email from a services vendor highlighting the candidate's resume match.
    Tone: professional, specific, value-focused. Include 2-3 portfolio bullet points if available.
    No preamble. Return just the email content.
    """
)

def build_email_chain(llm):
    return EMAIL_TEMPLATE | llm
