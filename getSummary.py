import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from the .env file
load_dotenv()

# Now you can access API_KEY_GEMINI
api_key = os.getenv("API_KEY_GEMINI")

genai.configure(api_key=os.environ["API_KEY_GEMINI"])

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
)

chat_session = model.start_chat(
  history=[
  ]
)

response = chat_session.send_message("What do you think of my input?")

print(response.text)


