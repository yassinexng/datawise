import os
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

async def ask_grok(context, question):
    key = os.getenv("GROK_API_KEY")
    if not key or key.strip() == "":
        return "Error: GROK_API_KEY not found in environment variables."

    try:
        client = Groq(api_key=key)
        prompt = f"""Role: Direct Data Scientist.
        Task: Answer the Query relying EXCLUSIVELY on the Context.
        Constraint: Zero hallucination. Output RAW JSON ONLY.
        If the answer is absent from the context, reply exactly: "Insufficient context."
        <context> {context}</context>
        <query> {question} </query>
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
    except Exception as e:
        error_str = str(e)
        if "429" in error_str:
            return "Error: Rate limit reached. Please wait a few minutes and try again."
        return f"Error: {error_str}"