import base64
import mimetypes
import os
import requests
from datetime import datetime
from google import genai
from google.genai import types

# GreenAPI credentials from GitHub secrets
ID_INSTANCE = os.environ.get("GREENAPI_ID")
API_TOKEN = os.environ.get("GREENAPI_TOKEN")
PHONE_NUMBER = os.environ.get("WHATSAPP_NUMBER")  # Receiver's WhatsApp number

PROMPTS = [
    "Generate a funny 'Good Morning' meme with a banana wearing sunglasses and drinking coffee.",
    "Create a cartoon of a cat yawning while holding a cup of chai that says 'Good Morning'.",
    "Make a penguin in pajamas brushing teeth with a sunrise background saying 'Good Morning!'.",
    "Generate a superhero potato waking up late for work with 'Good Morning' text.",
    "Create a dog riding a scooter delivering newspapers with 'Good Morning' written in the sky.",
    "Funny owl wearing glasses, sipping coffee, and reading the newspaper — caption 'Good Morning, Genius!'.",
    "Draw a smiling toast and a dancing egg wishing 'Good Morning' together.",
]

def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)
    print(f"File saved to: {file_name}")
    return file_name

def send_to_whatsapp(file_path, caption="Good Morning 🌞😂"):
    url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendFileByUpload/{API_TOKEN}"
    with open(file_path, "rb") as f:
        file_data = f.read()
    response = requests.post(
        url,
        files={"file": (os.path.basename(file_path), file_data)},
        data={"chatId": f"{PHONE_NUMBER}@c.us", "caption": caption},
    )
    print("WhatsApp Response:", response.json())

def get_daily_prompt():
    day_index = datetime.now().timetuple().tm_yday % len(PROMPTS)
    return PROMPTS[day_index]

def generate():
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    model = "gemini-2.5-flash-image-preview"
    prompt = get_daily_prompt()

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    config = types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
    file_index = 0
    for chunk in client.models.generate_content_stream(model=model, contents=contents, config=config):
        if not (chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts):
            continue
        part = chunk.candidates[0].content.parts[0]
        if part.inline_data and part.inline_data.data:
            file_name = f"goodmorning_{file_index}"
            file_index += 1
            file_extension = mimetypes.guess_extension(part.inline_data.mime_type)
            saved_file = save_binary_file(f"{file_name}{file_extension}", part.inline_data.data)
            send_to_whatsapp(saved_file, caption=f"🌞 Good Morning! {prompt}")
        else:
            print(chunk.text)

if __name__ == "__main__":
    generate()
