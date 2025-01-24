# Try implementing a basic RAG system -- will limit the usage of tokens and provide more accurate answers
# First, must find relevant research/data/context for the system to use.
# Maybe Focus on just one category, for now.



import requests
from bs4 import BeautifulSoup
import re
import json

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"

def get_ollama_response(prompt):
    """Get response from Ollama"""
    payload = {
        "model": "llama2", 
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_ENDPOINT, json=payload)
        return response.json()['response']
    except Exception as e:
        print(f"Error calling Ollama: {str(e)}")
        return f"Error: {str(e)}"

def extract_meaningful_text_from_html(html_content):
    """
    Extract meaningful text from HTML files
    """
    try:
        # Parse the HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script, style, and other non-content elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()

        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)
        return text[:10000]  # Limit to 10,000 characters
    
    except Exception as e:
        print(f"Error extracting text from HTML: {e}")
        return "Could not extract text from HTML file"

def analyze_data(questionnaire_data, instagram_data):
    """Analyze questionnaire and Instagram data using Ollama"""
    try:
        # Extract questionnaire responses
        questionnaire_text = questionnaire_data.get('content', '')
        responses = {}
        current_question = None
        for line in questionnaire_text.split('\n'):
            if line.startswith('Question: '):
                current_question = line[len('Question: '):].strip()
            elif line.startswith('Response: ') and current_question:
                responses[current_question] = line[len('Response: '):].strip()

        # Compile Instagram data for context
        instagram_context = []
        for key, file in instagram_data.items():
            if file:
                try:
                    # Read the file content
                    html_content = file.read().decode('utf-8')
                    
                    # Extract meaningful text
                    extracted_text = extract_meaningful_text_from_html(html_content)
                    
                    # Add to context
                    instagram_context.append(f"{key.capitalize()} file content: {extracted_text[:500]}...")
                except Exception as e:
                    print(f"Error processing {key} file: {e}")
        
        # Create prompts for analysis
        prompts = {
            "social_connection": f"""
            You are a digital wellbeing expert. Analyze the user's Instagram data and questionnaire responses about relationships.
            
            Questionnaire Response: {responses.get('How does Instagram help or hinder your relationships with friends, family, or your community?', 'No response provided')}
            
            Instagram Data Context:
            {' '.join(instagram_context)}
            
            Provide three specific, actionable recommendations for improving social connections on Instagram.
            Keep your response focused and practical, referencing the specific Instagram data where possible.
            """,
            
            "goal_focus": f"""
            You are a digital wellbeing expert. Analyze the user's Instagram data and questionnaire responses about personal growth.
            
            Questionnaire Response: {responses.get('How does the content you follow or engage with on Instagram inspire or motivate your personal or professional growth?', 'No response provided')}
            
            Instagram Data Context:
            {' '.join(instagram_context)}
            
            Provide three specific strategies for using Instagram more effectively for personal development.
            Keep your response focused and practical, referencing the specific Instagram data where possible.
            """,
            
            "self_worth": f"""
            You are a digital wellbeing expert. Analyze the user's Instagram data and questionnaire responses about self-esteem.
            
            Questionnaire Response: {responses.get('In what ways does Instagram impact your self-esteem or lead to comparisons with others?', 'No response provided')}
            
            Instagram Data Context:
            {' '.join(instagram_context)}
            
            Provide three specific strategies for maintaining healthy self-esteem while using Instagram.
            Keep your response focused and practical, referencing the specific Instagram data where possible.
            """,
            
            "moderation": f"""
            You are a digital wellbeing expert. Analyze the user's Instagram data and questionnaire responses about Instagram usage.
            
            Questionnaire Response: {responses.get('What strategies do you use to manage your time, set boundaries, or limit overwhelming content on Instagram?', 'No response provided')}
            
            Instagram Data Context:
            {' '.join(instagram_context)}
            
            Provide three specific recommendations for creating healthy boundaries and usage habits.
            Keep your response focused and practical, referencing the specific Instagram data where possible.
            """
        }

        # Generate insights
        insights = {}
        for section, prompt in prompts.items():
            print(f"\nGenerating insights for {section}...")
            insights[section] = get_ollama_response(prompt)

        return {
            "success": True,
            "insights": insights
        }

    except Exception as e:
        print(f"Error in analyze_data: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def process_files(questionnaire_file, instagram_files):
    """Process uploaded files and return insights"""
    try:
        print("Starting file processing")
        
        # Read questionnaire
        questionnaire_data = {}
        if questionnaire_file:
            try:
                questionnaire_text = questionnaire_file.read().decode('utf-8')
                questionnaire_data = {'content': questionnaire_text}
            except Exception as e:
                print(f"Error reading questionnaire file: {str(e)}")
                questionnaire_data = {}

        return analyze_data(questionnaire_data, instagram_files)

    except Exception as e:
        print(f"Error in process_files: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }