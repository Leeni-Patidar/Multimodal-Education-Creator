import io
import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
HF_IMAGE_MODEL = os.getenv("HF_IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell")

print(f"HF_API_KEY exists: {bool(HF_API_KEY)}")
print(f"Using image model: {HF_IMAGE_MODEL}")

if not HF_API_KEY:
    raise ValueError("HF_API_KEY not set")

client = InferenceClient(api_key=HF_API_KEY)
prompt = "Educational diagram of Photosynthesis, clean, labeled, high quality"

print("\nTesting image generation...")
print(f"Prompt: {prompt}\n")

image = client.text_to_image(prompt, model=HF_IMAGE_MODEL)
buffer = io.BytesIO()
image.save(buffer, format="PNG")

print(f"Success! Generated image size: {image.size}")
print(f"PNG bytes: {len(buffer.getvalue())}")
