import streamlit as st
import ollama
from typing import Optional

# Ensure the required modules are installed
try:
    import streamlit as st
    import ollama
except ModuleNotFoundError as e:
    st.error("Required module not found: {}. Please install it using 'pip install streamlit ollama'.".format(e.name))
    raise

# Define the slots for job description
def get_missing_slots(slots):
    return [slot for slot, value in slots.items() if value is None]

SLOT_QUESTIONS = {
    "company_name": "What is the company name?",
    "job_type": "What type of job is this?",
    "tech_stack": "What technical stack is required (e.g., Python, React, AWS)?",
    "experience": "What level of experience is needed?",
    "functionalities": "What are the main functionalities or responsibilities?",
    "location": "What is the job location?",
    "remark": "Any additional remarks?"
}

EXPERIENCE_LEVELS = ["Junior", "Mid-level", "Senior"]
JOB_TYPES = ["Full-time", "Part-time", "Contract"]

st.title("💼 Job Description Generator")
st.write("Fill in the job details below, and I'll generate a professional job description for you!")

if "slots" not in st.session_state:
    st.session_state.slots = {slot: None for slot in SLOT_QUESTIONS}
    st.session_state.messages = []

st.session_state.slots["company_name"] = st.text_input(SLOT_QUESTIONS["company_name"], key="company_name")
st.session_state.slots["job_type"] = st.selectbox(SLOT_QUESTIONS["job_type"], JOB_TYPES, key="job_type")
st.session_state.slots["experience"] = st.selectbox(SLOT_QUESTIONS["experience"], EXPERIENCE_LEVELS, key="experience")

for slot, question in SLOT_QUESTIONS.items():
    if slot not in ["company_name", "job_type", "experience"]:
        st.session_state.slots[slot] = st.text_input(question, key=slot)

if st.button("Submit"):
    if all(value is not None and value != "" for value in st.session_state.slots.values()):
        st.success("All job details are filled. Generating job description...")
        prompt = f"""
        Create a detailed professional job description based on the following information:
        - Company Name: {st.session_state.slots['company_name']}
        - Job Type: {st.session_state.slots['job_type']}
        - Tech Stack: {st.session_state.slots['tech_stack']}
        - Experience Level: {st.session_state.slots['experience']}
        - Main Functionalities/Responsibilities: {st.session_state.slots['functionalities']}
        - Location: {st.session_state.slots['location']}
        - Remark: {st.session_state.slots['remark']}
        
        The job description should include:
        1. Job Title (create an appropriate title)
        2. Job Summary
        3. Responsibilities
        4. Requirements
        5. Location and Job Type
        6. Nice-to-have skills (optional, infer from tech stack)
        """
        
        try:
            response = ollama.chat(
                model="deepseek-r1:1.5b",
                messages=[
                    {"role": "system", "content": "You are a professional HR assistant skilled in writing job descriptions."},
                    {"role": "user", "content": prompt}
                ]
            )
            job_description = response['message']['content']
            job_description = job_description.split("</think>")[-1].strip()  # Remove <think> content
            st.session_state.messages.append({"role": "assistant", "content": job_description})
        except Exception as e:
            job_description = f"Error generating job description: {str(e)}"

        st.subheader("Generated Job Description")
        st.markdown(job_description)
        
        if st.button("Save to File"):
            try:
                with open("job_description.md", "w") as f:
                    f.write(job_description)
                st.success("Job description saved to 'job_description.md'")
            except Exception as e:
                st.error(f"Failed to save file: {str(e)}")
    else:
        st.error("Please fill in all fields before submitting.")
