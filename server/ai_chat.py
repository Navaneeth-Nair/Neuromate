import os
import time
from datetime import datetime
from dotenv import load_dotenv
from google import genai as gai
from google.genai import types
from google.genai import errors
from safety_filter import check_and_filter

load_dotenv()

def response():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env")
        return

   
    try:
        with open("client_question.txt", "r", encoding="utf-8") as f:
            question = f.read().strip()
    except FileNotFoundError:
        print("client_question.txt not found.")
        return
    if not question:
        print("No question found.")
        return

    
    try:
        with open("ai_context.txt", "r", encoding="utf-8") as sysfile:
            system_instruction = sysfile.read().strip()
    except FileNotFoundError:
        system_instruction = "You are a helpful AI assistant."

    client = gai.Client(api_key=api_key)

    
    for attempt in range(3):
        try:
            geminiresponse = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(role="user", parts=[types.Part(text=question)])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction  
                )
            )
            break
        except errors.ClientError as e:
            if "RESOURCE_EXHAUSTED" in str(e):
                print(f"Rate limit hit. Retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)
            else:
                raise

    # Extract model response
    raw_text = geminiresponse.candidates[0].content.parts[0].text.strip()

    # Safety filter check
    blocked, filtered_text, category = check_and_filter(raw_text)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if blocked:
        print("Filtered Response Detected.")
        with open("filtered_response.txt", "a", encoding="utf-8") as s:
            s.write(f"[{timestamp}] : {filtered_text}\n")
        print(filtered_text)
    else:
        with open("response.txt",'w', encoding='utf-8') as res:
            res.write(raw_text.strip())
        with open("logging.txt", "a", encoding='utf-8') as log:
            log.write(f"[{timestamp}]: [{raw_text.strip()}]\n")


if __name__ == "__main__":
    response()
