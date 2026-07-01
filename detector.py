import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Load the Groq API key from the .env file
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Use the Groq language model to estimate whether a piece of writing appears AI-generated.
def get_llm_score(text):
# Prompt instructs the model to return only a numberbetween 0.0 (human) and 1.0 (AI).
    prompt = f"""
You are helping classify whether a text was likely written by AI or a human.

Return ONLY a number from 0.0 to 1.0.

0.0 means very likely human-written.
0.5 means uncertain.
1.0 means very likely AI-generated.

Text:
{text}
"""
# Call the Groq API
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        score_text = response.choices[0].message.content.strip()
        score = float(score_text)

        if score < 0:
            return 0.0
        if score > 1:
            return 1.0

        return score

# Return a neutral score if the API request fails
    except Exception as e:
        print("Groq error:", e)
        return 0.5