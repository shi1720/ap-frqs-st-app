# AP FRQ Evaluation App

## Overview

The AP FRQ Evaluation App is a powerful tool designed to assist educators and content creators in evaluating and improving Advanced Placement (AP) Free Response Questions (FRQs). This app uses advanced AI to analyze questions based on various criteria, ensuring they meet the rigorous standards required for AP exams.

**Live App**: [https://ap-frqs-st-app.streamlit.app/](https://ap-frqs-st-app.streamlit.app/)

## Features

- **Dual Input Methods**: 
  - Text input for individual FRQs
  - CSV upload for bulk processing

- **Comprehensive Evaluation**:
  - Clarity and structure analysis
  - Relevance and curriculum alignment assessment
  - Difficulty and grade level evaluation
  - Final holistic assessment

- **Detailed Feedback**: 
  - Individual scores for each evaluation aspect
  - Final evaluation with strengths and weaknesses
  - Actionable feedback for improvement

- **User-Friendly Interface**:
  - Interactive Streamlit app
  - Progress tracking for bulk processing
  - Downloadable results for CSV input

## How to Use

1. **Access the App**: 
   Visit [https://ap-frqs-st-app.streamlit.app/](https://ap-frqs-st-app.streamlit.app/)

2. **Enter API Key**:
   - Input your Anthropic API Key in the provided field
   - This key is required for the AI-powered evaluations

3. **Choose Input Method**:
   - **Text Input**: 
     - Enter FRQ and corresponding lesson plan
     - Add up to 3 FRQs
   - **CSV Upload**: 
     - Prepare a CSV file with columns: QUESTION, LESSON_PLAN
     - Upload the CSV file

4. **Process Questions**:
   - For text input, click "Evaluate FRQs"
   - For CSV upload, click "Process CSV"

5. **Review Results**:
   - Examine individual evaluation aspects
   - Check the final evaluation for overall quality
   - For CSV input, download the processed file with results

## Local Development

To run the app locally:

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the app:
   ```
   streamlit run app.py
   ```

## Security Note

The app requires an Anthropic API key for operation. This key is entered by the user and is not stored or logged by the application. Always keep your API key confidential.

## Feedback and Contributions

We welcome feedback and contributions to improve the AP FRQ Evaluation App. Please open an issue or submit a pull request on our GitHub repository.
