from google import genai as gai
from google.genai import types
from ai_safety import check_and_filter
from datetime import datetime

def response(self):
    client = gai.client(api_key=API_KEY)
    with open("ai_context.txt", "r", encoding="utf-8") as f:
        context = f.read().strip()

    with open("client_question.txt", "r", encoding="utf-8") as q:
        question = q.read().strip()
    
    geminiresponse = client.models.generate_content(
        model = "gemini-2.5-flash",
        config = types.GenerateContentConfig(
            thinking_config = types.ThinkingConfig(thinking_budget=0),
            system_instruction= context,
        ),
        contents= question
    )
    raw_text = geminiresponse.text or ""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    blocked, filtered_text, category = check_and_filter(raw_text)

    if blocked:
        print("Filtered")
        with open("filtered_response.txt","a", encoding="utf-8") as s:
            s.write(f"[{timestamp}] : ")
            s.write(filtered_text.strip() + "\n")
    
    else:
        print(raw_text)

    


    