import os
import time
from datetime import datetime
from dotenv import load_dotenv
from google import genai as gai
from google.genai import types
from google.genai import errors
from .safety_filter import check_and_filter
from .conversation_context import get_context

load_dotenv()

def response(additional_context: str = ""):
    """
    Generate AI response with conversation context
    
    Args:
        additional_context: Additional context to include (e.g., task list, mood info)
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env")
        print("Please create a .env file with: GEMINI_API_KEY=your_actual_api_key")
        return None
    
    # Check if API key is placeholder
    if api_key == "your_api_key_here" or len(api_key) < 20:
        print("\n" + "="*60)
        print("ERROR: Invalid or placeholder API key detected!")
        print("="*60)
        print("To fix this issue:")
        print("1. Get your Gemini API key from: https://makersuite.google.com/app/apikey")
        print("2. Open the .env file in this directory")
        print("3. Replace 'your_api_key_here' with your actual API key")
        print("   Format: GEMINI_API_KEY=your_actual_api_key_here")
        print("="*60 + "\n")
        return None

   
    try:
        with open("data/client_question.txt", "r", encoding="utf-8") as f:
            question = f.read().strip()
    except FileNotFoundError:
        print("client_question.txt not found.")
        return None
    if not question:
        print("No question found.")
        return None

    
    try:
        with open("data/ai_context.txt", "r", encoding="utf-8") as sysfile:
            system_instruction = sysfile.read().strip()
    except FileNotFoundError:
        system_instruction = "You are a helpful AI assistant."

    # Get conversation context
    context = get_context()
    conversation_history = context.get_context_string()
    
    # Build full context for AI
    full_context_parts = []
    if conversation_history:
        full_context_parts.append("Previous conversation:")
        full_context_parts.append(conversation_history)
        full_context_parts.append("")
    
    if additional_context:
        full_context_parts.append(additional_context)
        full_context_parts.append("")
    
    full_context_parts.append(f"Current user message: {question}")
    
    # Prepare conversation contents
    contents = []
    
    # Add conversation history as separate messages
    if conversation_history:
        # Parse history and add as separate messages
        history_lines = conversation_history.split("\n")
        current_role = None
        current_text = []
        
        for line in history_lines:
            if line.startswith("User:"):
                if current_role == "assistant" and current_text:
                    contents.append(types.Content(role="model", parts=[types.Part(text="\n".join(current_text))]))
                    current_text = []
                current_role = "user"
                current_text.append(line.replace("User:", "").strip())
            elif line.startswith("Assistant:"):
                if current_role == "user" and current_text:
                    contents.append(types.Content(role="user", parts=[types.Part(text="\n".join(current_text))]))
                    current_text = []
                current_role = "assistant"
                current_text.append(line.replace("Assistant:", "").strip())
            elif current_text:
                current_text.append(line.strip())
        
        # Add last message
        if current_text:
            if current_role == "user":
                contents.append(types.Content(role="user", parts=[types.Part(text="\n".join(current_text))]))
            else:
                contents.append(types.Content(role="model", parts=[types.Part(text="\n".join(current_text))]))
    
    # Add current question
    contents.append(types.Content(role="user", parts=[types.Part(text=question)]))

    client = gai.Client(api_key=api_key)

    
    for attempt in range(3):
        try:
            geminiresponse = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction  
                )
            )
            break
        except errors.ClientError as e:
            error_str = str(e)
            # Check for rate limit errors
            if "RESOURCE_EXHAUSTED" in error_str:
                if attempt < 2:  # Only retry if not last attempt
                    print(f"Rate limit hit. Retrying in {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)
                    continue
                else:
                    print("Rate limit exceeded. Please try again later.")
                    return None
            # Check for invalid API key errors
            elif any(keyword in error_str for keyword in ["API key not valid", "API_KEY_INVALID", "INVALID_ARGUMENT", "400"]):
                print("\n" + "="*60)
                print("ERROR: Invalid Gemini API Key!")
                print("="*60)
                print("The API key in your .env file is not valid or has expired.")
                print("\nTo fix this:")
                print("1. Get a valid API key from: https://makersuite.google.com/app/apikey")
                print("   OR visit: https://aistudio.google.com/app/apikey")
                print("2. Open the .env file in this directory")
                print("3. Update GEMINI_API_KEY with your actual key")
                print("   Format: GEMINI_API_KEY=AIzaSy...")
                print("="*60 + "\n")
                return None
            else:
                # Other API errors - don't retry, just fail
                print(f"\nAPI Error occurred: {error_str}")
                print("Failed to get response from Gemini API.")
                return None

    # Extract model response
    if not geminiresponse.candidates or not geminiresponse.candidates[0].content.parts:
        print("Error: No response generated from Gemini API.")
        return None
    
    raw_text = geminiresponse.candidates[0].content.parts[0].text.strip()

    # Safety filter check
    blocked, filtered_text, category = check_and_filter(raw_text)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if blocked:
        print("Filtered Response Detected.")
        with open("data/filtered_response.txt", "a", encoding="utf-8") as s:
            s.write(f"[{timestamp}] : {filtered_text}\n")
        print(filtered_text)
        response_text = filtered_text
        # Also write to response.txt so TTS can speak it
        with open("data/response.txt", 'w', encoding='utf-8') as res:
            res.write(response_text)
    else:
        response_text = raw_text.strip()
        with open("data/response.txt",'w', encoding='utf-8') as res:
            res.write(response_text)
    
    # Add to conversation context
    context.add_exchange(question, response_text)
    
    return response_text


if __name__ == "__main__":
    response()
