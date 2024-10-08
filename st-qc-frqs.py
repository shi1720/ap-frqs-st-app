import streamlit as st
import pandas as pd
import requests
import json
import time
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
import base64
from streamlit_lottie import st_lottie
from streamlit_extras.add_vertical_space import add_vertical_space
import threading

# Constants
API_URL = "https://api.anthropic.com/v1/messages"

# Helper functions
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def call_claude_api(prompt, api_key):
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 8192,
        "temperature": 0.6,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['content'][0]['text']
    else:
        st.error(f"API call failed with status code: {response.status_code}")
        st.error(f"Response: {response.text}")
        return None

def parallel_api_calls(prompts, api_key):
    responses = [None] * len(prompts)
    with ThreadPoolExecutor(max_workers=7) as executor:
        future_to_index = {executor.submit(call_claude_api, prompt, api_key): i for i, prompt in enumerate(prompts)}

        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                responses[index] = future.result()
            except Exception as exc:
                st.error(f'Prompt {index} generated an exception: {exc}')
                responses[index] = f"Error: {exc}"

    for i, response in enumerate(responses):
        if response is None:
            st.warning(f"Warning: No response received for prompt {i}")
            responses[i] = "No response received"

    return responses
    
MULTI_SHOT_EXAMPLES = """{
  "questions": [
    {
      "level": "Question Level",
      "detail": "Question",
      "expectation": "The question is not ambiguous. There is only one interpretation and enough information is provided to correctly respond to the question if you have studied the topic. There are not multiple interpretations of the question",
      "examples": [
        {
          "question": "The painting shows the Emperor Qianlong is dressed as a Tibetan Buddhist teacher (lama). The Bodhisattva Manjusri is a major figure worshiped in the Tibetan Buddhist religious tradition. Which of the following is an example of a religious policy most similar to the one represented by the painting?\n\nA Spanish colonial authorities forcing the conversion of Native Americans to Christianity\nB European rulers participating in religious wars during the Protestant Reformation\nC Mughal rulers sponsoring Hindu learning and conversing with Hindu preachers\nD Merchants and Sufi mystics helping to spread Islam into Southeast Asia and sub-Saharan Africa",
          "pass": true,
          "reason": "The question relies on the readers broader understanding of the topic, but does provide the context and reference needed to know which is the correct response."
        },
        {
          "question": "What is the average atomic mass of chlorine based on the given isotopic masses and their relative abundances?\nA 35.438 amu\nB 34.968 amu\nC 36.000 amu\nD  37.500 amu\n",
          "pass": false,
          "reason": "The question suggests that the isotopic mass and relative abundance is offered, but it is not provided. The student could not calculate a value without this data."
        },
        {
          "question": "In a chemical reaction, if 0.5 moles of a reactant decompose to produce a product, how many molecules of the product are formed? (Use Avogadro's number, which is approximately $6.022 \\times 10^{23}$ molecules/mole) \na 3.01 x 10^23 molecules\nb 6.02 x 10^23 molecules\nc 4.01 x 10^23 molecules\nd 1.00 x 10^24 molecules\n",
          "pass": false,
          "reason": "The answer to this question is dependent on the stoichiometry of the deomposition"
        },
        {
          "question": "Question: What was the primary purpose of the tribute system developed by the Song Dynasty?\nA. To deter aggressors through the display of wealth\nB. To promote cultural exchange with neighboring states\nC. To support the funding of public projects\nD. To prevent internal conflicts within the Dynasty",
          "pass": true,
          "reason": "The question relies on the student's understanding of the material to respond. There is only one interpretation of the question, enough context is provided to choose the correct response."
        }
      ]
    }
  ]
}

"""

def generate_prompt1(QUESTION):
    return f"""
You are the world's leading expert in AP assessment design across all subjects, with 30 years of experience in crafting unambiguous, high-quality questions. Your task is to evaluate the clarity and structure of the given AP Free Response Question (FRQ).

FRQ to evaluate: {QUESTION}

Multi-shot examples for reference:
{MULTI_SHOT_EXAMPLES}

Instructions:
1. Analyze the FRQ meticulously, considering its applicability across all AP subjects.
2. Evaluate the question's clarity and structure based on these criteria:
   a. Unambiguity: The question must have only one clear interpretation. A good FRQ may have multiple correct responses when a student is asked to connect concepts of their choosing.
   b. Completeness: All necessary information must be provided that a well prepared student would need to respond to the question (e.g. if the student is to given values, the values are given) and additional materials should not be provided for underprepared students.
   c. Precision: The task must be explicitly stated with a clear, subject-specific verb. It is GOOD if students are given general topics and can decide which aspects of the overall theme they want to write about.
   d. Appropriate Context: Relevant historical, scientific, or literary context must be provided if required.
   e. Language Appropriateness: Vocabulary and phrasing must be suitable for AP-level students across subjects.
   f. Structural Integrity: For multi-part questions, each part must be clearly delineated and logically connected.

3. Follow these steps for your evaluation:
   Step 1: Identify the subject-specific task verb and analyze its clarity.
   Step 2: Assess the question's singularity of interpretation.
   Step 3: Verify the presence of all necessary information that a well prepared student would need to answer the question.
   Step 4: Evaluate the precision of the stated task.
   Step 5: Check for appropriate context provision.
   Step 6: Analyze vocabulary and phrasing suitability.
   Step 7: For multi-part questions, evaluate the structure and logical flow.

4. Critical Thinking: Consider potential misinterpretations or areas of confusion for students.

5. Decision Making: The FRQ passes (score 1) if and only if it meets ALL criteria effectively. Any failure in a single aspect results in a fail (score 0).

6. Return ONLY a JSON object with this structure:
   {{
     "score": 0 or 1,
     "rationale": "Two-line explanation of your evaluation, addressing the most critical aspects",
     "feedback": "Two-line constructive feedback for improvement, if necessary"
   }}

Attention: Strict adherence to JSON format is required. Any deviation will result in severe penalties. Your evaluation must reflect the highest standards in AP assessment design across all subjects.
"""

def generate_prompt2(QUESTION, LESSON_PLAN):
    return f"""
As the foremost authority on AP curriculum development across all subjects, with 30 years of experience in aligning assessments with educational standards, your task is to evaluate the relevance and alignment of the given Free Response Question (FRQ) to AP curricula.

FRQ to evaluate: {QUESTION}
AP Lesson Plan: {LESSON_PLAN}

Multi-shot examples for reference:
{MULTI_SHOT_EXAMPLES}

Instructions:
1. Conduct a comprehensive analysis of the FRQ and the provided AP Lesson Plan, considering its applicability across AP subjects.
2. Assess the FRQ's relevance and alignment based on these universal AP criteria:
   a. Conceptual Alignment: The question must align with key concepts and themes in the AP curriculum.
   b. Skill Integration: Relevant subject-specific and cross-disciplinary skills must be incorporated.
   c. Content Appropriateness: The question must cover appropriate topics for the AP level.
   d. Cognitive Demand: The question should require higher-order thinking skills appropriate for AP.
   e. Curriculum Coverage: The FRQ should address significant aspects of the AP curriculum.

3. Follow these evaluation steps:
   Step 1: Identify the key concepts and skills addressed in the FRQ.
   Step 2: Cross-reference these with the AP Lesson Plan.
   Step 3: Assess the depth and breadth of curriculum coverage.
   Step 4: Evaluate the cognitive demand of the question.
   Step 5: Analyze how well the FRQ integrates multiple curriculum aspects.

4. Critical Thinking: Consider how effectively the FRQ promotes higher-order thinking within the AP framework.

5. Decision Making: The FRQ passes (score 1) if and only if it meets ALL relevance and alignment criteria effectively. Any significant misalignment results in a fail (score 0).

6. Return ONLY a JSON object with this structure:
   {{
     "score": 0 or 1,
     "rationale": "Two-line explanation of your evaluation, focusing on curriculum alignment and skill integration",
     "feedback": "Two-line constructive feedback for improving alignment, if necessary"
   }}

Attention: Strict adherence to JSON format is required. Any deviation will result in severe penalties. Your evaluation must reflect the highest standards in AP curriculum alignment across all subjects.
"""

def generate_prompt3(QUESTION):
    return f"""
As a world-renowned cognitive psychologist and educational assessment expert with 30 years of experience across all academic disciplines, your task is to determine the difficulty, question type, and appropriate grade level for the given AP question.

Question to evaluate: {QUESTION}

Multi-shot examples for reference:
{MULTI_SHOT_EXAMPLES}

Instructions:
1. Conduct a multi-faceted analysis of the question:
   a. Identify the precise AP task verb.
   b. Map the cognitive processes required to Bloom's Taxonomy and DOK levels.
   c. Outline the step-by-step approach to answering the question.

2. Categorize the question's difficulty using these universal criteria:
   - Easy: Bloom's (Remembering, Understanding), DOK (1-2)
     Task verbs: Define, Identify, List, State, Describe, Summarize, Interpret, Illustrate, Compare, Estimate
   - Moderate: Bloom's (Applying, Analyzing), DOK (3)
     Task verbs: Analyze, Apply, Calculate, Classify, Contrast, Demonstrate, Determine, Develop, Differentiate, Examine, Explain, Formulate, Investigate, Justify, Organize, Predict, Relate, Solve, Use
   - Difficult: Bloom's (Evaluating, Creating), DOK (4)
     Task verbs: Appraise, Argue, Assess, Compose, Conclude, Construct, Create, Critique, Design, Evaluate, Generate, Hypothesize, Invent, Judge, Plan, Produce, Propose, Recommend, Revise, Synthesize, Validate

3. Determine the most appropriate grade level:
   Options: K-5, 6-8, 9-10, 11-12, AP, college level introductory courses
   Consider:
   - Number and complexity of steps required
   - Cognitive demand of each step
   - Subject-specific knowledge prerequisites
   - Sophistication of the task verb

4. Critical Thinking: Evaluate how the question's difficulty aligns with AP standards across subjects.

5. Return ONLY a JSON object with this structure:
   {{
     "difficulty": "Easy/Moderate/Difficult",
     "question_type": "Identified AP task verb",
     "grade_level": "Determined grade level",
     "rationale": "Two-line explanation for the difficulty and grade level assessment"
   }}

Attention: Strict adherence to JSON format is required. Any deviation will result in severe penalties. Your assessment must reflect a nuanced understanding of cognitive demands across all AP subjects.
"""

def generate_final_prompt(QUESTION, PROMPT_RESULTS):
    return f"""
As the world's preeminent expert in AP assessment with 30 years of experience revolutionizing standardized testing across all subjects, your task is to provide the definitive evaluation of an AP question's suitability for inclusion in AP exams.

Question to evaluate: {QUESTION}

Previous evaluation results:
{PROMPT_RESULTS}

Instructions:
1. Score Calculation:
   Sum the scores from the prompts (excluding the difficulty/grade level prompt). The maximum sum is 2.

2. Conduct a holistic review, examining all aspects of the question, previous evaluations, and the calculated sum score.

3. Identify 2-3 key strengths based on the highest-scoring aspects from previous evaluations.

4. Identify 2-3 key weaknesses based on the lowest-scoring aspects and any critical issues raised.

5. Make your final determination based on these criteria:
   a. Overall quality and alignment with AP standards across subjects
   b. Balance of strengths and weaknesses
   c. Potential impact on student assessment and learning
   d. The calculated sum score (out of 2)
   e. Uniqueness and non-duplication of content
   f. Appropriateness of question type for the content being tested
   g. Consistency with AP-level depth and complexity

6. Scoring:
   Assign a final score of 1 if and based on the following conditions:
   - The sum score is 2 out of 2 OR The only missing points are related to the explanation
   - The question demonstrates exceptional quality and strong alignment with AP standards
   - Any identified weaknesses are minor and do not significantly impact the question's effectiveness
   - The question is unique and not duplicative of other content
   - The question type is appropriate for the content being tested
   - The question and explanations are consistent with AP-level depth and complexity
   Assign a score of 0 if ANY of the above conditions are not met.

7. Return ONLY a JSON object with this structure:
   {{
     "sum_score": calculated sum (0-2),
     "final_score": 0 or 1,
     "rationale": "Two-line explanation for your final scoring decision",
     "feedback": "Two-line actionable feedback for improvement or commendation",
     "key_strengths": [
       "Strength 1",
       "Strength 2",
       "Strength 3" (optional)
     ],
     "key_weaknesses": [
       "Weakness 1",
       "Weakness 2",
       "Weakness 3" (optional)
     ]
   }}

Attention: Strict adherence to JSON format is required. Any deviation will result in severe penalties. Your evaluation must reflect the highest standards in AP assessment across all subjects and provide clear insights for validating or improving AP exam questions.
"""
def process_row(row_data, api_key, prompt_states, edited_prompts):
    QUESTION, LESSON_PLAN = row_data

    def format_prompt(prompt_template, **kwargs):
        for key, value in kwargs.items():
            prompt_template = prompt_template.replace(f"{{{{{key}}}}}", str(value))
        return prompt_template

    prompts = [
        format_prompt(edited_prompts['prompt1'], QUESTION=QUESTION) if prompt_states["prompt1"] else None,
        format_prompt(edited_prompts['prompt2'], QUESTION=QUESTION, LESSON_PLAN=LESSON_PLAN) if prompt_states["prompt2"] else None,
        format_prompt(edited_prompts['prompt3'], QUESTION=QUESTION) if prompt_states["prompt3"] else None,
    ]

    # Filter out None values (disabled prompts)
    prompts = [p for p in prompts if p is not None]

    responses = parallel_api_calls(prompts, api_key)

    # Prepare PROMPT_RESULTS
    PROMPT_RESULTS = "<evaluation_results>\n"
    for i, response in enumerate(responses):
        PROMPT_RESULTS += f"<evaluation_{i+1}>\n{response}\n</evaluation_{i+1}>\n"
    PROMPT_RESULTS += "</evaluation_results>"

    final_prompt = format_prompt(edited_prompts['final_prompt'], QUESTION=QUESTION, PROMPT_RESULTS=PROMPT_RESULTS)
    final_response = call_claude_api(final_prompt, api_key)

    return responses + [final_response]

def get_csv_download_link(df, filename="processed_frqs.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download Processed CSV</a>'
    return href

def process_csv(df, api_key, start_row, end_row, progress_bar, stop_flag, download_button, prompt_states, edited_prompts):
    results = []
    for index, row in df.iloc[start_row:end_row+1].iterrows():
        if stop_flag.is_set():
            break
        try:
            row_data = row.tolist()
            responses = process_row(row_data, api_key, prompt_states, edited_prompts)
            results.append(responses)
        except Exception as e:
            st.error(f"Error processing row {index}: {str(e)}")
            results.append(["NA"] * 4)  # Add NA for all 4 columns
        
        # Update the DataFrame after each row is processed
        for j, response in enumerate(results[-1][:3]):
            df.loc[index, f'Evaluation_{j+1}'] = response
        df.loc[index, 'Final_Evaluation'] = results[-1][3]
        
        progress = (index - start_row + 1) / (end_row - start_row + 1)
        progress_bar.progress(progress)
        
        # Update the download button after each row
        download_button.markdown(get_csv_download_link(df), unsafe_allow_html=True)
    
    return results

def main():
    st.set_page_config(page_title="AP FRQ Evaluation", page_icon="📝", layout="wide")

    # Load Lottie animation
    lottie_book = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_1a8dx7zj.json")

    # Title and animation
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title("AP FRQ Evaluation")
        st.write("Evaluate your AP Free Response Questions with ease!")
    with col2:
        st_lottie(lottie_book, speed=1, height=150, key="initial")

    # API Key input
    api_key = st.text_input("Enter your Anthropic API Key:", type="password")
    if not api_key:
        st.warning("Please enter your Anthropic API Key to proceed.")
        return

    # Prompt editing and enabling/disabling
    st.header("Prompts Configuration")
    prompt_states = {}
    edited_prompts = {}

    for i in range(1, 4):
        st.subheader(f"Prompt {i}")
        prompt_states[f"prompt{i}"] = st.checkbox(f"Enable Prompt {i}", value=True)
        
        if i == 1:
            default_prompt = generate_prompt1("{{QUESTION}}")
        elif i == 2:
            default_prompt = generate_prompt2("{{QUESTION}}", "{{LESSON_PLAN}}")
        elif i == 3:
            default_prompt = generate_prompt3("{{QUESTION}}")
        
        edited_prompts[f"prompt{i}"] = st.text_area(f"Edit Prompt {i}", value=default_prompt, height=400)

    st.subheader("Final Prompt")
    default_final_prompt = generate_final_prompt("{{QUESTION}}", "{{PROMPT_RESULTS}}")
    edited_prompts["final_prompt"] = st.text_area("Edit Final Prompt", value=default_final_prompt, height=400)

    # Input method selection
    input_method = st.radio("Choose input method:", ("Text Input", "CSV Upload"))

    if input_method == "Text Input":
        questions = []
        for i in range(3):  # Allow up to 3 questions
            st.subheader(f"FRQ {i+1}")
            question = st.text_area(f"Enter FRQ {i+1}", key=f"q{i}")
            lesson_plan = st.text_area(f"Enter lesson plan for FRQ {i+1}", key=f"l{i}")
            
            if question and lesson_plan:
                questions.append([question, lesson_plan])
            
            if i < 2:  # Don't show "Add another question" for the last question
                add_another = st.checkbox(f"Add another FRQ", key=f"add{i}")
                if not add_another:
                    break

        if st.button("Evaluate FRQs"):
            if questions:
                with st.spinner("Evaluating FRQs..."):
                    results = []
                    progress_bar = st.progress(0)
                    for i, q in enumerate(questions):
                        result = process_row(q, api_key, prompt_states, edited_prompts)
                        results.append(result)
                        progress_bar.progress((i + 1) / len(questions))

                    for i, (question, result) in enumerate(zip(questions, results)):
                        st.subheader(f"Results for FRQ {i+1}")
                        st.write(f"**Question:** {question[0]}")
                        
                        for j, response in enumerate(result[:3]):
                            if prompt_states[f"prompt{j+1}"]:
                                with st.expander(f"Evaluation {j+1}"):
                                    st.json(json.loads(response))
                        
                        with st.expander("Final Evaluation"):
                            st.json(json.loads(result[-1]))
            else:
                st.warning("Please enter at least one FRQ to evaluate.")

    if input_method == "CSV Upload":
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write(df)

            # Row range selection
            col1, col2 = st.columns(2)
            with col1:
                start_row = st.number_input("Start Row", min_value=0, max_value=len(df)-1, value=0)
            with col2:
                end_row = st.number_input("End Row", min_value=start_row, max_value=len(df)-1, value=len(df)-1)

            if st.button("Process CSV"):
                progress_bar = st.progress(0)
                stop_flag = threading.Event()
                
                # Create placeholders for pause button and download button
                pause_button = st.empty()
                download_button = st.empty()
                
                def pause_processing():
                    stop_flag.set()
                    st.warning("Processing paused. You can download the CSV with processed rows so far.")
                    # Ensure the download button is visible when paused
                    download_button.markdown(get_csv_download_link(df), unsafe_allow_html=True)

                pause_button.button("Pause Processing", on_click=pause_processing)

                with st.spinner("Processing CSV..."):
                    results = process_csv(df, api_key, start_row, end_row, progress_bar, stop_flag, download_button, prompt_states, edited_prompts)

                if stop_flag.is_set():
                    st.success("Processing paused. You can download the CSV with processed rows above.")
                else:
                    st.success("Processing completed. You can download the full CSV above.")

                st.write(df)

if __name__ == "__main__":
    main()
