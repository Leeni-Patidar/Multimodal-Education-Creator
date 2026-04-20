import io
import logging
import os
import textwrap
from typing import List

from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from PIL import Image, ImageDraw

load_dotenv()
logger = logging.getLogger(__name__)

HF_API_KEY = os.getenv("HF_API_KEY")
HF_IMAGE_MODEL = os.getenv("HF_IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell")

VARIANT_THEMES = [
    {
        "bg_top": (240, 245, 255),
        "bg_bottom": (205, 225, 255),
        "border": "#2563eb",
        "accent": "#3b82f6",
        "title": "Concept Overview",
    },
    {
        "bg_top": (245, 252, 255),
        "bg_bottom": (214, 242, 230),
        "border": "#059669",
        "accent": "#10b981",
        "title": "Visual Explanation",
    },
    {
        "bg_top": (255, 248, 240),
        "bg_bottom": (255, 228, 204),
        "border": "#ea580c",
        "accent": "#f97316",
        "title": "Key Idea Diagram",
    },
]


def generate_placeholder_image(prompt: str, variant_index: int = 0) -> bytes:
    """Generate a simple educational placeholder image using PIL."""
    try:
        width, height = 800, 600
        theme = VARIANT_THEMES[variant_index % len(VARIANT_THEMES)]
        img = Image.new("RGB", (width, height), color="white")
        draw = ImageDraw.Draw(img)

        for y in range(height):
            blend = y / height
            r = int(theme["bg_top"][0] * (1 - blend) + theme["bg_bottom"][0] * blend)
            g = int(theme["bg_top"][1] * (1 - blend) + theme["bg_bottom"][1] * blend)
            b = int(theme["bg_top"][2] * (1 - blend) + theme["bg_bottom"][2] * blend)
            draw.rectangle([(0, y), (width, y + 1)], fill=(r, g, b))

        draw.rectangle([(10, 10), (width - 10, height - 10)], outline=theme["border"], width=3)
        draw.text((40, 40), f"{theme['title']} #{variant_index + 1}", fill=theme["border"], font=None)

        prompt_text = f"Topic: {prompt[:120]}"
        lines = textwrap.wrap(prompt_text, width=60)
        y_pos = 120
        for line in lines:
            draw.text((30, y_pos), line, fill="#374151", font=None)
            y_pos += 30

        draw.rounded_rectangle([(90, 320), (710, 470)], radius=18, outline=theme["accent"], width=3)
        draw.text((120, 350), "Educational diagram preview", fill=theme["accent"], font=None)
        draw.text((120, 385), f"Variation {variant_index + 1} of the requested concept", fill="#4b5563", font=None)
        draw.text((120, 420), "Fallback image generated locally", fill="#6b7280", font=None)
        draw.text((30, height - 60), "Generated with Concept Visualizer AI", fill="#6b7280", font=None)

        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        return img_bytes.getvalue()
    except Exception as e:
        logger.error(f"Error generating placeholder image: {str(e)}")
        raise


def _generate_image_with_hf(prompt: str) -> bytes | None:
    """Generate a single image with Hugging Face when credentials are available."""
    if not HF_API_KEY:
        return None

    try:
        logger.info(f"Attempting to generate image with Hugging Face model: {HF_IMAGE_MODEL}")
        client = InferenceClient(api_key=HF_API_KEY)
        image = client.text_to_image(prompt, model=HF_IMAGE_MODEL)

        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        logger.info("Image generated successfully with Hugging Face")
        return img_bytes.getvalue()
    except Exception as e:
        logger.warning(f"Hugging Face image generation failed: {str(e)}")

    return None


def generate_images(prompt: str, count: int = 5) -> List[bytes]:
    """
    Generate multiple images in order with fallback to placeholder.
    
    Preserves image order by processing sequentially instead of using
    as_completed(), ensuring images appear in the correct positions.
    """
    total = max(5, count)
    images: List[bytes] = []

    for index in range(total):
        variant_prompt = f"{prompt}. Variation {index + 1}."
        try:
            image_bytes = _generate_image_with_hf(variant_prompt)
            if image_bytes:
                images.append(image_bytes)
            else:
                if not HF_API_KEY and index == 0:
                    logger.warning("HF_API_KEY not set, using local placeholder images")
                images.append(generate_placeholder_image(prompt, index))
        except Exception as e:
            logger.error(f"Failed to generate image at index {index}: {str(e)}")
            images.append(generate_placeholder_image(prompt, index))

    return images


def generate_image(prompt: str) -> bytes:
    """Backward-compatible single-image wrapper."""
    return generate_images(prompt, count=1)[0]
