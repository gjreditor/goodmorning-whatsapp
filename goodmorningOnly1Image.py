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

# Rotating prompts for daily variation
PROMPTS = [
    "Draw a smiling toast and a dancing egg wishing 'Good Morning' together.",
    "Create a cartoon of a cat yawning while holding a cup of chai that says 'Good Morning'.",
    "Make a penguin in pajamas brushing teeth with a sunrise background saying 'Good Morning!'.",
    "Generate a superhero potato waking up late for work with 'Good Morning' text.",
    "Create a dog riding a scooter delivering newspapers with 'Good Morning' written in the sky.",
    "Funny owl wearing glasses, sipping coffee, and reading the newspaper — caption 'Good Morning, Genius!'.",
    "Generate a banana wearing sunglasses and drinking coffee to say 'Good Morning'.",
]

def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)
    print(f"File saved to: {file_name}")
    return file_name

def send_to_whatsapp(file_path, caption="🌞 Good Morning!"):
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

    # Ask Gemini for both: funny image + caption
    prompt = f"""{get_daily_prompt()}
Also write a short, funny WhatsApp caption (under 10 words) that matches the image and says Good Morning."""

    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
    config = types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])

    caption_text = None
    image_saved = False

    for chunk in client.models.generate_content_stream(model=model, contents=contents, config=config):
        if not (chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts):
            continue

        for part in chunk.candidates[0].content.parts:
            # If Gemini returned text (caption)
            if part.text and not caption_text:
                caption_text = part.text.strip()
                print("Generated Caption:", caption_text)

            # If Gemini returned image (first one only)
            elif part.inline_data and part.inline_data.data and not image_saved:
                file_extension = mimetypes.guess_extension(part.inline_data.mime_type)
                file_name = f"goodmorning{file_extension}"
                saved_file = save_binary_file(file_name, part.inline_data.data)

                # Send once we have a caption
                send_to_whatsapp(saved_file, caption=caption_text or "🌞 Good Morning!")
                image_saved = True
                return  # stop after first image

if __name__ == "__main__":
    generate()
