
#pip install google-genai
from google import genai
import os
from dotenv import load_dotenv
load_dotenv()


api_key=os.getenv("api_key")

#step1=authenticate
client= genai.Client(api_key=api_key)

prompt="what is ai agent in simple words"

response=client.models.generate_content(
    model="gemini-3.5-flash",
    contents=prompt
)

print(response.text)