import requests

class GeminiService:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_custom_response(self, prompt):
        # Simulate sending prompt to an API
        response = requests.post("https://example.com/gemini", json={"prompt": prompt})
        return response.json().get("response", "No response from Gemini API.")
